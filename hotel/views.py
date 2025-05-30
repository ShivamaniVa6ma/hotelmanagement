from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib import messages
from .models import UserMap
from hotelapp.models import Tax as HotelTax
from hotelapp.models import Room, Booking,Guest,ContactMessage,Facility,AboutUs,FAQ,Spa,RoomImage,Service,RoomType,Event
from hotelapp.forms import RoomForm,BulkRoomForm, BookingForm,GuestForm,TeamMember, ContactForm,AvailabilityForm
from datetime import datetime,timedelta
import json
from decimal import Decimal
from django.db.models import Q
import logging
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from subscription.models import SubscriptionUserDetails
from django.contrib.auth.decorators import login_required
from hotelapp.models import LogoSettings
logger = logging.getLogger(__name__)
from hotelapp.utils import generate_invoice_id
from subscription.models import Tax as SubscriptionTax
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from io import BytesIO

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def company_detail(request, company_name):
    # Retrieve the subscription user details based on the company name
    subscription_user = get_object_or_404(SubscriptionUserDetails, company_name=company_name)
    
    # Render a template with the subscription user details
    return render(request, 'company_detail.html', {'subscription_user': subscription_user})

@login_required
def base_view(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()
    
    if subscription_user:
        logo_settings = LogoSettings.objects.filter(subscription_user=subscription_user)
    else:
        logo_settings = None

    # Debugging: Print values in the console
    print("Subscription User:", subscription_user)
    print("Logo Settings:", logo_settings)
    if logo_settings:
        print("Logo Settings:", logo_settings)
        print("Site Name:", logo_settings.site_name)
    else:
        print("No Logo Settings found.")

    return render(request, 'base.html', {
        "site_name": logo_settings.site_name if logo_settings and logo_settings.site_name else "Bloom UP",
        "favicon_url": logo_settings.favicon.url if logo_settings and logo_settings.favicon else None,
        "light_logo_url": logo_settings.light_logo.url if logo_settings and logo_settings.light_logo else None,
        "dark_logo_url": logo_settings.dark_logo.url if logo_settings and logo_settings.dark_logo else None,
        "subscription_user_id": subscription_user.id  # Pass the subscription_user_id
    })
# @require_POST
# def check_availability(request):
#     try:
#         data = json.loads(request.body)
#         check_in = data.get('check_in')
#         check_out = data.get('check_out')
#         room_type = data.get('room_type')
#         # bed_type = data.get('bed_type')
#         # ac_type = data.get('ac_type')

#         # Convert check-in and check-out to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
#         check_out_date = timezone.datetime.strptime(check_out, "%Y-%m-%dT%H:%M")

#         # Query to find available rooms
#         available_rooms = Room.objects.filter(is_available=True).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         # Apply filters
#         if room_type:
#             available_rooms = available_rooms.filter(room_type=room_type)
#         # if bed_type:
#         #     available_rooms = available_rooms.filter(bed_type=bed_type)
#         # if ac_type:
#         #     available_rooms = available_rooms.filter(ac_type=ac_type)

#         return JsonResponse({
#             'success': True,
#             'available_rooms': list(available_rooms.values('id', 'room_type', 'base_price'))
#         })

#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })

def check_availability(request, company_name):
    subscription_user = request.subscription_user

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            room_type = form.cleaned_data['room_type']

            if check_in >= check_out:
                return JsonResponse({'error': 'Check-out must be after check-in.'}, status=400)

            rooms = Room.objects.filter(subscription_user=subscription_user, is_available=True)

            if room_type:
                rooms = rooms.filter(room_type__name=room_type)

            available_rooms = rooms.exclude(
                bookings__check_in__lt=check_out,
                bookings__check_out__gt=check_in
            ).distinct()

            # Pass the form data to the checkout template
            return render(request, 'hotel/checkout.html', {
                'available_rooms': available_rooms,
                'check_in': check_in,
                'check_out': check_out,
                'room_type': room_type,
                'company_name': company_name,
                'subscription_user': subscription_user
            })
        else:
            return JsonResponse({'error': 'Invalid date format. Please use the correct format.'}, status=400)

    return redirect('user-panel:index', company_name=company_name)


def calculate_total_price(room, check_in, check_out, return_breakdown=False):
    # Parse string datetimes if needed
    if isinstance(check_in, str):
        check_in_dt = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
    else:
        check_in_dt = check_in

    if isinstance(check_out, str):
        check_out_dt = datetime.strptime(check_out, "%Y-%m-%dT%H:%M")
    else:
        check_out_dt = check_out

    # Make timezone-aware if not already
    if timezone.is_naive(check_in_dt):
        check_in_dt = timezone.make_aware(check_in_dt)
    if timezone.is_naive(check_out_dt):
        check_out_dt = timezone.make_aware(check_out_dt)

    total_price = Decimal('0.0')
    daily_breakdown = []

    total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600

    holiday_events = Event.objects.filter(
        Q(start_date__lte=check_out_dt.date()) & Q(end_date__gte=check_in_dt.date())
    )

    holiday_dates = set()
    for event in holiday_events:
        current = event.start_date
        while current <= event.end_date:
            holiday_dates.add(current)
            current += timedelta(days=1)

    current_date = check_in_dt.date()
    last_full_date = check_out_dt.date() if total_hours >= 24 else check_in_dt.date()

    while current_date < last_full_date:
        if current_date in holiday_dates:
            price = room.holiday_price
            reason = "Holiday"
        elif current_date.weekday() >= 5:
            price = room.weekend_price
            reason = "Weekend"
        else:
            price = room.base_price
            reason = "Weekday"

        price = Decimal(price)
        daily_breakdown.append({
            "date": str(current_date),
            "price": float(price),
            "reason": reason
        })

        total_price += price
        current_date += timedelta(days=1)

    # Handle extra hours after full days
    hourly_applied = False
    if total_hours < 24:
        # Less than 1 full day
        hourly_price = Decimal(str(total_hours)) * room.hourly_price
        day_price = Decimal(room.base_price)
        total_price = hourly_price if total_hours < 10 else day_price
        hourly_applied = total_hours < 10
    else:
        # Handle leftover hours beyond full days
        combined_dt = datetime.combine(current_date, check_in_dt.time())
        if timezone.is_naive(combined_dt):
            combined_dt = timezone.make_aware(combined_dt)

        leftover_seconds = (check_out_dt - combined_dt).total_seconds()
        extra_hours = leftover_seconds / 3600

        if extra_hours > 0:
            if extra_hours < 10:
                hourly_price = Decimal(str(extra_hours)) * room.hourly_price
                hourly_applied = True
                total_price += hourly_price
                daily_breakdown.append({
                    "date": str(current_date),
                    "price": float(hourly_price),
                    "reason": f"Extra {extra_hours:.2f} hours (Hourly)"
                })
            else:
                full_day_price = Decimal(room.base_price)
                total_price += full_day_price
                daily_breakdown.append({
                    "date": str(current_date),
                    "price": float(full_day_price),
                    "reason": "Extra >10 hrs (Full day)"
                })

    result = {
        "room_id": room.id,
        "room_number": room.room_number,
        "daily_breakdown": daily_breakdown,
        "hourly_applied": hourly_applied,
        "block": room.block,
        "final_price": round(float(total_price), 2)
    }

    return result if return_breakdown else round(float(total_price), 2)

@login_required
@transaction.atomic
@require_POST
def create_booking(request, company_name):
    subscription_user = request.subscription_user

    # ✅ 1. Handle guest creation or reuse
    if request.user.is_guest and hasattr(request.user, 'guest_profile'):
        guest = request.user.guest_profile
    else:
        guest_form = GuestForm(request.POST, request.FILES)
        if not guest_form.is_valid():
            return JsonResponse({'error': 'Invalid guest information'}, status=400)
        guest = guest_form.save(commit=False)
        guest.subscription_user = subscription_user
        guest.save()

    # ✅ 2. Begin booking transaction
    with transaction.atomic():
        booking_form = BookingForm(request.POST)
        if not booking_form.is_valid():
            return JsonResponse({'error': 'Invalid booking information'}, status=400)

        try:
            booking_data = booking_form.save(commit=False)
            booking_data.guest = guest
            booking_data.subscription_user = subscription_user

            selected_rooms = json.loads(request.POST.get('selectedRooms', '[]'))
            if not selected_rooms:
                return JsonResponse({'error': 'No rooms selected'}, status=400)

            base_total_amount = Decimal('0.00')
            bookings = []

            for room_id in selected_rooms:
                room = Room.objects.select_for_update().get(id=room_id)

                overlap_exists = Booking.objects.filter(
                    room=room,
                    check_in__lt=booking_data.check_out,
                    check_out__gt=booking_data.check_in
                ).exists()

                if overlap_exists:
                    raise ValueError(f"Room {room.room_number} is already booked during the selected period.")

                room_price = calculate_total_price(room, booking_data.check_in, booking_data.check_out)
                if not isinstance(room_price, Decimal):
                    room_price = Decimal(str(room_price))  # Ensure Decimal
                base_total_amount += room_price

                new_booking = Booking(
                    guest=guest,
                    room=room,
                    check_in=booking_data.check_in,
                    check_out=booking_data.check_out,
                    adults=booking_data.adults,
                    children=booking_data.children,
                    payment_type='razorpay',
                    payment_status='pending',
                    total_amount=room_price,  # Will adjust after tax
                    subscription_user=subscription_user
                )
                bookings.append(new_booking)

                room.is_available = False
                room.save()

            # ✅ 3. Calculate applicable taxes
            total_tax_amount = Decimal('0.00')

            # Global platform fees (is_platform_fee=True, no subscription_user)
            platform_taxes = SubscriptionTax.objects.filter(is_platform_fee=True)

            # Subscription-specific taxes (is_platform_fee=False)
            hotel_taxes = HotelTax.objects.filter(subscription_user=subscription_user)

            # Combine and calculate
            all_taxes = list(platform_taxes) + list(hotel_taxes)

            for tax in all_taxes:
                tax_amount = (base_total_amount * tax.percentage) / Decimal('100')
                total_tax_amount += tax_amount

            grand_total = base_total_amount + total_tax_amount

            # ✅ 4. Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                'amount': int(grand_total * 100),  # in paisa
                'currency': 'INR',
                'payment_capture': '1'
            })

            # ✅ 5. Update booking total amounts proportionally
            for booking in bookings:
                proportion = booking.total_amount / base_total_amount if base_total_amount > 0 else Decimal('0.00')
                tax_share = total_tax_amount * proportion
                booking.total_amount += tax_share
                booking.razorpay_order_id = razorpay_order['id']
                booking.save()

                send_invoice_email(booking, request)

            return JsonResponse({
                'success': True,
                'payment_details': {
                    'key_id': settings.RAZORPAY_KEY_ID,
                    'order_id': razorpay_order['id'],
                    'amount': razorpay_order['amount'],
                    'currency': razorpay_order['currency'],
                    'booking_id': bookings[0].id if bookings else None,
                    'guest_name': guest.name,
                    'guest_email': guest.email,
                    'guest_phone': guest.phone
                }
            })

        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': f"Booking failed: {str(e)}"}, status=500)


def send_invoice_email(booking, request):
    invoice_url = request.build_absolute_uri(
        reverse('admin-panel:invoice_detail', kwargs={'invoice_id': booking.invoice_id})
    )
    subscription_user = booking.subscription_user
    company_name = getattr(subscription_user, 'company_name', None)
    print("company_name for invoice email:", company_name)  # Debug print

    context = {
        'booking': booking,
        'guest': booking.guest,
        'subscription_user': subscription_user,
        'invoice_url': invoice_url,
        'company_name': company_name,
    }
    html_message = render_to_string('hotelapp/email_invoice.html', context)
    plain_message = strip_tags(html_message)
    
   
    
    # Create email
    email = EmailMessage(
        subject=f'Invoice for Booking #{booking.invoice_id}',
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.guest.email],
        # attachments=[
        #     ('invoice.pdf', pdf.read(), 'application/pdf')
        # ]
    )
    email.content_subtype = "html"
    email.send()
@csrf_exempt
def get_price_estimate(request, company_name):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            check_in = data["check_in"]
            check_out = data["check_out"]
            selected_rooms = data["selectedRooms"]

            total_price = 0
            room_breakdown = []

            for room_id in selected_rooms:
                room = Room.objects.get(id=room_id)
                result = calculate_total_price(room, check_in, check_out, return_breakdown=True)
                room_breakdown.append(result)
                total_price += result['final_price']

            return JsonResponse({
                "success": True,
                "total_price": round(total_price, 2),
                "room_breakdown": room_breakdown
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def send_booking_invoice(booking):
    guest = booking.guest
    room = booking.room
    room_type = room.room_type
    company = booking.subscription_user

    if not guest.email:
        print(f"❌ Guest email is missing for booking ID {booking.id}")
        return

    # Get logo if allowed
    logo_url = settings.DEFAULT_LOGO_URL
    if company.subscription_plan and getattr(company.subscription_plan, 'is_logo_change', False):
        logo = company.logosettings_set.first()
        if logo and logo.dark_logo:
            logo_url = logo.dark_logo.url

    # Get room image
    room_image = ''
    if hasattr(room, 'images') and room.images.exists():
        first_image = room.images.first()
        if first_image and hasattr(first_image, 'image'):
            room_image = first_image.image.url
    else:
        room_image = settings.DEFAULT_ROOM_IMAGE

    # Render invoice template
    html_content = render_to_string('invoice_template.html', {
        'booking': booking,
        'guest': guest,
        'room': room,
        'room_type': room_type,
        'company': company,
        'room_image': room_image,
        'logo_url': logo_url
    })

    try:
        print(f"📧 Sending booking invoice to {guest.email} for booking ID {booking.id}")
        email = EmailMessage(
            subject=f'Your Booking Invoice - {booking.invoice_id}',
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[guest.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        print(f"✅ Invoice email sent successfully to {guest.email}")
    except Exception as e:
        print(f"❌ Failed to send email to {guest.email}: {e}")



# @require_POST
# @transaction.atomic
# def create_booking(request, company_name):
#     subscription_user = request.subscription_user

#     guest_form = GuestForm(request.POST, request.FILES)
#     booking_form = BookingForm(request.POST)

#     logger.info("Received booking request")

#     if guest_form.is_valid() and booking_form.is_valid():
#         try:
#             guest = guest_form.save()
#             booking = booking_form.save(commit=False)
#             booking.guest = guest

#             selected_rooms = json.loads(request.POST.get('selectedRooms', '[]'))
#             logger.info(f"Selected rooms: {selected_rooms}")
            
#             if not selected_rooms:
#                 logger.warning("No rooms selected")
#                 return JsonResponse({'error': 'No rooms selected'}, status=400)

#             total_amount = 0
#             bookings = []
            
#             # Calculate total amount and create bookings
#             for room_data in selected_rooms:
#                 room_id = room_data['id']
#                 room = Room.objects.select_for_update().get(id=room_id)
                
#                 if not room.is_available:
#                     logger.warning(f"Room {room.room_number} is not available")
#                     raise ValueError(f'Room {room.room_number} is no longer available.')

#                 total_amount += room.base_price
                
#                 selected_rooms.add(room.room_type.id)  # If needed to track selected room types

#             # Create Razorpay order
#             razorpay_order = client.order.create({
#                 'amount': int(total_amount * 100),  # Amount in paise
#                 'currency': 'INR',
#                 'payment_capture': '1'
#             })

#             # Create bookings with pending payment status
#             for room_data in selected_rooms:
#                 room_id = room_data['id']
#                 room = Room.objects.get(id=room_id)
                
#                 new_booking = Booking(
#                     guest=guest,
#                     room=room,
#                     check_in=booking.check_in,
#                     check_out=booking.check_out,
#                     adults=booking.adults,
#                     children=booking.children,
#                     payment_type='razorpay',
#                     payment_status='pending',
#                     total_amount=room.base_price,
#                     razorpay_order_id=razorpay_order['id']
#                 )
#                 bookings.append(new_booking)
#                 room.is_available = False
#                 room.save()

#             created_bookings = Booking.objects.bulk_create(bookings)
#             first_booking_id = created_bookings[0].id if created_bookings else None

#             # Return payment details to frontend
#             return JsonResponse({
#                 'success': True,
#                 'payment_details': {
#                     'key_id': settings.RAZORPAY_KEY_ID,
#                     'order_id': razorpay_order['id'],
#                     'amount': razorpay_order['amount'],
#                     'currency': razorpay_order['currency'],
#                     'booking_id': first_booking_id,
#                     'guest_name': guest.name,
#                     'guest_email': guest.email,
#                     'guest_phone': guest.phone
#                 }
#             })

#         except Exception as e:
#             logger.error(f"Error in create_booking: {str(e)}")
#             transaction.set_rollback(True)
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         errors = {}
#         if not guest_form.is_valid():
#             errors['guest_form'] = guest_form.errors
#         if not booking_form.is_valid():
#             errors['booking_form'] = booking_form.errors
#         logger.error(f"Form validation errors: {errors}")
#         return JsonResponse({'error': 'Invalid form data', 'errors': errors}, status=400)

def booking_success(request, company_name,booking_id):
    subscription_user = request.subscription_user

    booking_id = request.GET.get('booking_id')
    print(f"Booking ID: {booking_id}")
    return render(request, 'hotel/booking_success.html', {'booking_id': booking_id, 'company_name':company_name})

def booking_failed(request, company_name):
    subscription_user = request.subscription_user

    booking_id = request.GET.get('booking_id')
    return render(request, 'hotel/booking_failed.html', {'booking_id': booking_id, 'company_name':company_name})

# @transaction.atomic
# def create_booking(request):
#     if request.method == 'POST':
#         try:
#             post_data = request.POST.copy()
#             selected_rooms = json.loads(post_data.get('selectedRooms', '[]'))

#             guest_form = GuestForm(post_data, request.FILES)
#             booking_form = BookingForm(post_data)

#             if not guest_form.is_valid():
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Invalid guest information',
#                     'errors': guest_form.errors
#                 })

#             if not booking_form.is_valid():
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Invalid booking information',
#                     'errors': booking_form.errors
#                 })

#             # Save guest
#             guest = guest_form.save()

#             bookings = []
#             total_amount = 0

#             for room_data in selected_rooms:
#                 room_type = room_data['roomType']
#                 room_count = int(room_data['roomCount'])
#                 ac_type = room_data['acType']
#                 bed_type = room_data.get('bedType')

#                 query = Room.objects.filter(
#                     room_type=room_type,
#                     ac_type=ac_type,
#                     is_available=True
#                 )

#                 if bed_type:
#                     query = query.filter(bed_type=bed_type)

#                 available_rooms = query.exclude(
#                     booking__check_out__gt=booking_form.cleaned_data['check_in'],
#                     booking__check_in__lt=booking_form.cleaned_data['check_out']
#                 )[:room_count]

#                 if len(available_rooms) < room_count:
#                     raise ValidationError(f"Not enough {room_type} rooms available")

#                 for room in available_rooms:
#                     booking = Booking(
#                         guest=guest,
#                         room=room,
#                         check_in=booking_form.cleaned_data['check_in'],
#                         check_out=booking_form.cleaned_data['check_out'],
#                         adults=booking_form.cleaned_data['adults'],
#                         children=booking_form.cleaned_data['children'],
#                         payment_type=booking_form.cleaned_data['payment_type'],
#                         total_amount=room.base_price
#                     )
#                     bookings.append(booking)
#                     total_amount += room.base_price

#             Booking.objects.bulk_create(bookings)

#             return JsonResponse({
#                 'success': True,
#                 'message': f'Successfully booked {len(bookings)} rooms',
#                 'redirect_url': '/booking-confirmation/'
#             })

#         except ValidationError as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'An error occurred: {str(e)}'
#             })

#     return JsonResponse({'error': 'Invalid request method'}, status=400)

# def booking_view(request):
#     if request.method == 'POST':
#         guest_form = GuestForm(request.POST)
#         booking_form = BookingForm(request.POST)
#         room_selection_form = RoomSelectionForm(request.POST)
        
#         if guest_form.is_valid() and booking_form.is_valid() and room_selection_form.is_valid():
#             guest = guest_form.save()
#             booking = booking_form.save(commit=False)
#             booking.guest = guest
            
#             selected_rooms = json.loads(request.POST.get('selectedRooms', '[]'))
#             total_amount = 0
            
#             for room_data in selected_rooms:
#                 room_type = room_data['roomType']
#                 room = Room.objects.filter(room_type=room_type, is_available=True).first()
#                 if room:
#                     booking_instance = Booking.objects.create(
#                         guest=guest,
#                         room=room,
#                         check_in=booking.check_in,
#                         check_out=booking.check_out,
#                         adults=booking.adults,
#                         children=booking.children,
#                         total_amount=room.price
#                     )
#                     total_amount += room.price
#                     room.is_available = False
#                     room.save()
            
#             return JsonResponse({'success': True, 'total_amount': total_amount})
#         else:
#             return JsonResponse({'success': False, 'errors': {
#                 'guest_form': guest_form.errors,
#                 'booking_form': booking_form.errors,
#                 'room_selection_form': room_selection_form.errors
#             }})
#     else:
#         guest_form = GuestForm()
#         booking_form = BookingForm()
#         room_selection_form = RoomSelectionForm()
    
#     rooms = Room.objects.filter(is_available=True)
#     context = {
#         'guest_form': guest_form,
#         'booking_form': booking_form,
#         'room_selection_form': room_selection_form,
#         'rooms': rooms
#     }
#     return render(request, 'hotel/troom3.html', context)


# def check_availability(request):
#     available_rooms = None  # Initialize available_rooms

#     if request.method == 'POST':
#         check_in_date = request.POST.get('check_in')
#         check_out_date = request.POST.get('check_out')
#         room_type = request.POST.get('room_type')

#         # Convert to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in_date, '%Y-%m-%dT%H:%M')
#         check_out_date = timezone.datetime.strptime(check_out_date, '%Y-%m-%dT%H:%M')

#         # Query to find available rooms based on filters
#         available_rooms = Room.objects.filter(is_available=True).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         # Apply room type filter if selected
#         if room_type:
#             available_rooms = available_rooms.filter(room_type=room_type)

#     return render(request, 'hotelapp/rooms1.html', {
#         'available_rooms': available_rooms,  # Pass available rooms if any
#         'check_in': check_in_date if request.method == 'POST' else None,
#         'check_out': check_out_date if request.method == 'POST' else None,
#         'room_type': room_type,
#     })

# def check_availability(request):
#     available_rooms = None
#     check_in_date = None
#     check_out_date = None
#     guest_id = request.GET.get('guest_id') or request.POST.get('guest_id')  # Get guest_id from either GET or POST

#     if request.method == 'POST':
#         check_in = request.POST.get('check_in')
#         check_out = request.POST.get('check_out')
#         room_types = ['standard', 'deluxe', 'vip', 'conference']  # Add this line
#         # Convert to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in, '%B %d, %Y%I:%M %p')
#         check_out_date = timezone.datetime.strptime(check_out, '%B %d, %Y%I:%M %p')

#         # Query to find available rooms
#         available_rooms = Room.objects.filter(is_available=True).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         if room_types:
#             available_rooms = available_rooms.filter(room_type=room_types)

#         # Store the data in the session or pass it as a query parameter for the redirect
#         request.session['check_in'] = check_in_date.strftime('%B %d, %Y%I:%M %p')
#         request.session['check_out'] = check_out_date.strftime('%B %d, %Y%I:%M %p')
#         request.session['available_rooms'] = list(available_rooms.values())
#         request.session['guest_id'] = guest_id
#         request.session['room_types'] = room_types

#         return render(request, 'hotel/available_rooms.html')

#     # Render the default index page if not a POST request
#     context = {
#         'available_rooms': available_rooms,
#         'guest_id': guest_id,
#     }

#     return render(request, 'hotel/index.html', context)


# In the redirected view
# def check_availability_page(request):
#     available_rooms = request.session.get('available_rooms', [])
#     check_in = request.session.get('check_in', None)
#     check_out = request.session.get('check_out', None)
#     guest_id = request.session.get('guest_id', None)
#     room_type = request.session.get('room_type', None)

#     context = {
#         'available_rooms': available_rooms,
#         'check_in': check_in,
#         'check_out': check_out,
#         'guest_id': guest_id,
#         'room_type': room_type,
#     }

#     return render(request, 'hotel/check_availability.html', context)


# def check_availability(request):
#     available_rooms = None
#     check_in_date = None
#     check_out_date = None
#     guest_id = request.GET.get('guest_id') or request.POST.get('guest_id')  # Get guest_id from either GET or POST

#     if request.method == 'POST':
#         check_in = request.POST.get('check_in')
#         check_out = request.POST.get('check_out')
#         room_type = request.POST.get('room_type')

#         # Convert to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in, '%B %d, %Y%I:%M %p')
#         check_out_date = timezone.datetime.strptime(check_out, '%B %d, %Y%I:%M %p')

#         # Query to find available rooms
#         available_rooms = Room.objects.filter(is_available=True).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         if room_type:
#             available_rooms = available_rooms.filter(room_type=room_type)

#     context = {
#         'available_rooms': available_rooms,
#         'guest_id': guest_id,  # Include guest_id in context
#         'room_type': room_type if request.method == 'POST' else None,
#         'check_in': check_in_date.strftime('%B %d, %Y%I:%M %p') if check_in_date else None,
#         'check_out': check_out_date.strftime('%B %d, %Y%I:%M %p') if check_out_date else None
#     }

#     return render(request, 'hotel/index.html', context)


def index(request, company_name):
    subscription_user = request.subscription_user

    rooms = Room.objects.filter(subscription_user=subscription_user) \
        .select_related('room_type') \
        .prefetch_related('images', 'features')

    facilities = list(Facility.objects.filter(subscription_user=subscription_user))
    print(f"Number of facilities: {facilities}")  # Add this line

    room_types = {}


    for room in rooms:
        room_type_name = room.room_type.name
        if room_type_name not in room_types:
            room_types[room_type_name] = {
                'room': room,
                'image': room.images.first().image.url if room.images.exists() else None,
                'features': room.features.all(),
            }
    dynamic_room_types = RoomType.objects.filter(subscription_user=subscription_user)

    context = {
        'room_type': dynamic_room_types,  # for dropdown
        'room_types': room_types.values(),  # Get the values for rendering
        'company_name': company_name,
        'subscription_user': subscription_user,  # Pass subscription_user if needed in the template
        'facilities': list(enumerate(facilities)),  # Use enumerate here
    }
    
    return render(request, 'hotel/index.html', context)

def room(request, company_name):
    subscription_user = request.subscription_user
    rooms = Room.objects.select_related('room_type') \
        .prefetch_related('images', 'features') \
        .filter(subscription_user=subscription_user)
    
    room_types = {}

    for room in rooms:
        room_type_name = room.room_type.name
        if room_type_name not in room_types:
            room_types[room_type_name] = {
                'room': room,
                'image': room.images.first().image.url if room.images.exists() else None,
                'features': room.features.all(),
            }

    context = {
        'room_types': room_types.values(),
        'company_name': company_name,
        'subscription_user': subscription_user
    }

    return render(request, 'hotel/room.html', context)



def about(request, company_name):
    subscription_user = request.subscription_user
    team_members = TeamMember.objects.filter(subscription_user=subscription_user)\
    .select_related('designation').all()
    facilities = Facility.objects.filter(subscription_user=subscription_user)
    about_list = AboutUs.objects.filter(subscription_user=subscription_user)


    context={
        'company_name': company_name,
        'team_members': team_members,
        'facilities': facilities,
        'about_list': about_list,

        'subscription_user': subscription_user  # Add subscription_user to context if needed
    }
    # Render the about.html template
    return render(request, 'hotel/about.html', context)

@ensure_csrf_cookie
def contact_view(request, company_name):
    subscription_user = None

    # If user is logged in
    if request.user.is_authenticated:
        try:
            subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)
        except SubscriptionUserDetails.DoesNotExist:
            subscription_user = None

    # Fallback: Get by company_name if user is not authenticated
    if not subscription_user:
        try:
            subscription_user = SubscriptionUserDetails.objects.get(company_name__iexact=company_name, is_active=True)
        except SubscriptionUserDetails.DoesNotExist:
            subscription_user = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            if subscription_user:
                contact.subscription_user = subscription_user
            contact.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Thank You for providing feedback to us!'
                })
            else:
                return redirect('contact')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                })

    # Get embed code
    embed_code = ""
    if subscription_user:
        try:
            user_map = UserMap.objects.get(subscription_user=subscription_user)
            embed_code = user_map.embed_code
        except UserMap.DoesNotExist:
            pass

    context = {
        'form': ContactForm(),
        'company_name': company_name,
        'embed_code': embed_code,
        'subscription_user': subscription_user,
    }

    return render(request, 'hotel/contact.html', context)



def booking(request, company_name):
    subscription_user = request.subscription_user

    # Render the booking.html template
    return render(request, 'hotel/booking.html', {'company_name': company_name})

def team(request, company_name):
    subscription_user = request.subscription_user

    team_members = TeamMember.objects.filter(subscription_user=subscription_user) \
        .select_related('designation').all()

    context={
        'company_name': company_name,
        'team_members': team_members,
        'subscription_user': subscription_user
    }
    # Render the team.html template
    return render(request, 'hotel/team.html', context)

# def facilities(request, company_name):
#     subscription_user = request.subscription_user

#     facilities = Facility.objects.filter(subscription_user=subscription_user)

#     context = {
#         'facilities': facilities,
#     }
#     # Render the facilities.html template
#     return render(request, 'hotel/facilities.html', {'company_name': company_name})

def facilities_view(request, company_name):
    # Get the subscription user
    subscription_user = request.subscription_user
    
    # Get all facilities for this subscription user
    facilities = Facility.objects.filter(subscription_user=subscription_user)
    
    context = {
        'company_name': company_name,
        'subscription_user': subscription_user,  # Add subscription_user to context if needed

        'facilities': facilities,
    }
    return render(request, 'hotel/facilities.html', context)


def frequently_asked_questions(request, company_name):
    subscription_user = request.subscription_user
    faqs = FAQ.objects.filter(subscription_user=subscription_user).order_by('created_at')

    context = {
        'faqs': faqs,
        'company_name': company_name
    }
    # Render the frequently_asked_questions.html template
    return render(request, 'hotel/faq.html', context)

def services(request, company_name):
    subscription_user = request.subscription_user
    services= Service.objects.filter(subscription_user=subscription_user).order_by('created_at')
    
    context = {
        # 'spa': spa,
        'company_name': company_name,
        'services': services
    }
    # Render the services.html template
    return render(request, 'hotel/services.html', context)

def spa(request, company_name):
    subscription_user = request.subscription_user
    spa = Spa.objects.filter(subscription_user=subscription_user).order_by('created_at')
    faqs = FAQ.objects.filter(subscription_user=subscription_user).order_by('created_at')

    context = {
        'spa': spa,
        'company_name': company_name,
        'faqs': faqs

    }
    # Render the spa.html template
    return render(request, 'hotel/spa.html',context)

def checkout(request, company_name):
    subscription_user = request.subscription_user

    # Render the checkout.html template
    return render(request, 'hotel/checkout.html', {'company_name': company_name})


def room_details(request, company_name):
    subscription_user = request.subscription_user

    # Render the room_details.html template
    return render(request, 'hotel/room-details.html', {'company_name': company_name})

# def room_two(request, company_name):
#     subscription_user = request.subscription_user

#     # Render the room_two.html template
#     return render(request, 'hotel/room-2.html', {'company_name': company_name})

def gallery(request, company_name):
    subscription_user = request.subscription_user
    room_images = RoomImage.objects.filter(subscription_user= subscription_user)[:9]
    spa = Spa.objects.filter(subscription_user=subscription_user)[:8]
    facilities=Facility.objects.filter(subscription_user=subscription_user)[:8]
    about_us=AboutUs.objects.filter(subscription_user=subscription_user)[:8]
    services = Service.objects.filter(subscription_user=subscription_user)[:8]

    context={
        'room_images':room_images,
        'spa':spa,
        'facilities':facilities,
        'services':services,
        'about_us':about_us,
        'company_name':company_name
    }

    # Render the gallery.html template
    return render(request, 'hotel/gallery.html', context)

def restaurant(request, company_name):
    subscription_user = request.subscription_user

    # Render the restaurant.html template
    return render(request, 'hotel/restaurant.html', {'company_name': company_name})

def fetch_seating_capacities(request,company_name):
    room_type_id = request.GET.get('room_type_id')
    if not room_type_id:
        return JsonResponse({'error': 'Room type ID is required'}, status=400)

    seating_capacities = Room.objects.filter(room_type_id=room_type_id).values_list('seating_capacity', flat=True).distinct()
    return JsonResponse({'seating_capacities': list(seating_capacities)})

def fetch_bed_types(request, company_name):
    room_type_id = request.GET.get("room_type_id")

    if not room_type_id:
        return JsonResponse({"error": "Room type ID is required"}, status=400)

    try:
        bed_types = Room.objects.filter(room_type_id=room_type_id).values_list("bed_type", flat=True).distinct()
        return JsonResponse({"bed_types": list(bed_types)})

    except Room.DoesNotExist:
        return JsonResponse({"error": "No bed types found"}, status=404)


def fetch_rooms(request, company_name):
    room_type_id = request.GET.get('room_type_id')
    bed_type = request.GET.get('bed_type')
    seating_capacity_filter = request.GET.get('seating_capacity')
    ac_type = request.GET.get('ac_type')
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')

    if not room_type_id or not check_in_str or not check_out_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        check_in = datetime.strptime(check_in_str, "%Y-%m-%dT%H:%M")
        check_out = datetime.strptime(check_out_str, "%Y-%m-%dT%H:%M")
        if check_in >= check_out:
            return JsonResponse({'error': 'Invalid check-in/check-out range'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    subscription_user = SubscriptionUserDetails.objects.filter(
        company_name=company_name, is_active=True
    ).first()
    if not subscription_user:
        return JsonResponse({'error': 'Subscription user not found'}, status=404)

    room_type = get_object_or_404(RoomType, id=room_type_id, subscription_user=subscription_user)

    rooms = Room.objects.filter(room_type=room_type, subscription_user=subscription_user)

    if room_type.bed_type.lower() == "conference" and seating_capacity_filter:
        rooms = rooms.filter(seating_capacity=seating_capacity_filter)
    elif bed_type:
        rooms = rooms.filter(bed_type=bed_type)

    if ac_type:
        rooms = rooms.filter(ac_type=ac_type)

    # ✨ Refined overlap logic
    overlapping_rooms = Booking.objects.filter(
        check_in__lt=check_out,
        check_out__gt=check_in
    ).values_list('room_id', flat=True)

    # ✅ Available rooms = Rooms not in overlapping bookings
    available_rooms = rooms.exclude(id__in=overlapping_rooms)

    room_data = [
        {
            'room_id': room.id,
            'room_number': room.room_number,
            'block': room.block,
            'bed_type': room.bed_type,
            'ac_type': room.ac_type,
            'seating_capacity': room.seating_capacity,
            'is_available': True,
        }
        for room in available_rooms
    ]

    print("DEBUG: Room availability fetched successfully.")
    return JsonResponse({'room_data': room_data})




# def contact_us(request, company_name):
#     subscription_user = request.subscription_user

#     # Render the contact_us.html template
#     return render(request, 'hotel/contact.html', {'company_name': company_name})

# def availability_view(request):
#     # Call the check_availability view
#     response = check_availability(request)
    
#     # Return the response from check_availability
#     return response

# def fetch_rooms(request):
#     if request.method == 'GET':
#         room_types = request.GET.getlist('room_type')
#         print("Received room types:", room_types)  # Debugging line
#         response_data = []

#         for room_type in room_types:
#             rooms = Room.objects.filter(room_type=room_type).values(
#                 'id', 'room_number', 'base_price'
#             )
#             print("Rooms for type", room_type, ":", list(rooms))  # Debugging line
#             for room in rooms:
#                 room['is_booked'] = Booking.objects.filter(room_id=room['id'], check_out__gt=timezone.now()).exists()
#             response_data.append({
#                 'room_type': room_type,
#                 'rooms': list(rooms)
#             })

#         print("Response data:", response_data)  # Debugging line
#         return JsonResponse(response_data, safe=False)
#     return JsonResponse({'error': 'Invalid request'}, status=400)            


# def fetch_rooms(request):
#     if request.method == 'GET':
#         room_types = request.GET.getlist('room_type[]')
#         bed_type = request.GET.get('bed_type')
        
#         # Base query
#         rooms_query = Room.objects.filter(room_type__in=room_types)
        
#         # Apply bed type filter if provided and not conference room
#         if bed_type and 'conference' not in room_types:
#             rooms_query = rooms_query.filter(bed_type=bed_type)
            
#         # Get all matching rooms
#         rooms = rooms_query.values('id', 'room_number', 'room_type', 'ac_type', 'is_available', 'bed_type')
        
#         # Organize rooms by type and AC status
#         response_data = {}
#         for room_type in room_types:
#             response_data[room_type] = {
#                 'ac': [],
#                 'nonAc': []
#             }
            
#             # Filter rooms for this type
#             type_rooms = [r for r in rooms if r['room_type'] == room_type]
            
#             # Separate AC and non-AC rooms
#             for room in type_rooms:
#                 if room['ac_type'] == 'ac':
#                     response_data[room_type]['ac'].append({
#                         'id': room['id'],
#                         'room_number': room['room_number'],
#                         'is_available': room['is_available'],
#                         'bed_type': room['bed_type']
#                     })
#                 else:
#                     response_data[room_type]['nonAc'].append({
#                         'id': room['id'],
#                         'room_number': room['room_number'],
#                         'is_available': room['is_available'],
#                         'bed_type': room['bed_type']
#                     })
                    
#         return JsonResponse(response_data)
        
#     return JsonResponse({'error': 'Invalid request'}, status=400)

# def fetch_rooms(request):
#     subscription_user = request.subscription_user

#     if request.method == 'GET':
#         room_types = request.GET.getlist('room_type[]')
#         bed_type = request.GET.get('bed_type')
#         seating_capacity = request.GET.get('seating_capacity')
#         check_in = request.GET.get('check_in')
#         check_out = request.GET.get('check_out')

#         # Base query
#         rooms_query = Room.objects.filter(room_type__in=room_types)

#         # Filter by bed type if provided and not conference room
#         if bed_type and 'conference' not in room_types:
#             rooms_query = rooms_query.filter(bed_type=bed_type)

#         # Filter by seating capacity for conference rooms
#         if seating_capacity and 'conference' in room_types:
#             rooms_query = rooms_query.filter(seating_capacity=seating_capacity)

#         # Filter out booked rooms
#         if check_in and check_out:
#             booked_rooms = Booking.objects.filter(
#                 Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
#             ).values_list('room_id', flat=True)
#             rooms_query = rooms_query.exclude(id__in=booked_rooms)

#         # Fetch matching rooms
#         rooms = rooms_query.values('id', 'room_number', 'room_type', 'ac_type', 'is_available', 'seating_capacity')

#         # Organize rooms by type and attribute
#         response_data = {}
#         for room_type in room_types:
#             response_data[room_type] = {
#                 'ac': [],
#                 'nonAc': []
#             }
#             type_rooms = [r for r in rooms if r['room_type'] == room_type]
#             for room in type_rooms:
#                 room_data = {
#                     'id': room['id'],
#                     'room_number': room['room_number'],
#                     'is_available': room['is_available']
#                 }
#                 if room_type == 'conference':
#                     room_data['seating_capacity'] = room['seating_capacity']

#                 if room['ac_type'] == 'ac':
#                     response_data[room_type]['ac'].append(room_data)
#                 else:
#                     response_data[room_type]['nonAc'].append(room_data)

#         return JsonResponse(response_data)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


def fetch_room_prices(request):
    subscription_user = request.subscription_user

    room_type = request.GET.get('room_type')
    if room_type:
        rooms = Room.objects.filter(room_type=room_type)
        if rooms.exists():
            prices = {
                'base_price': rooms[0].base_price,
                'weekend_price': rooms[0].weekend_price,
                'holiday_price': rooms[0].holiday_price, 
                'hourly_price': rooms[0].hourly_price,
            }
            return JsonResponse({'prices': prices})
        else:
            return JsonResponse({'error': 'Room type not found'}, status=404)
    return JsonResponse({'error': 'Room type not specified'}, status=400)


@csrf_exempt
def payment_callback(request, company_name):
    if request.method == "POST":
        data = request.POST
    else:
        data = request.GET  # Razorpay may redirect using GET
    razorpay_order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')
    signature = data.get('razorpay_signature')

    try:
        razorpay_client.utility.verify_payment_signature({
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
            })

            # ✅ Handle all bookings for that order
        bookings = Booking.objects.filter(razorpay_order_id=razorpay_order_id)
        invoice_id = generate_invoice_id()

        for booking in bookings:
                booking.payment_status = 'success'
                booking.status = 'confirmed'
                booking.invoice_id = invoice_id
                booking.razorpay_payment_id = payment_id
                booking.save()

                # ✅ Send individual invoice
                send_booking_invoice(booking)

        return redirect('user-panel:booking_success', company_name=company_name, booking_id=bookings.first().id)

    except Exception as e:
        print("Payment verification failed:", e)
        return redirect('user-panel:booking_failed', company_name=company_name)

def booking_success(request, company_name):
    subscription_user = request.subscription_user

    booking_id = request.GET.get('booking_id')
    return render(request, 'hotel/booking_success.html', {'booking_id': booking_id, 'company_name':company_name})

        
def booking_failed(request, company_name):
    error_message = request.GET.get('error', 'Payment failed. Please try again.')
    return render(request, 'hotel/booking_failed.html', {
        'company_name': company_name,
        'error_message': error_message
    })


def privacy(request,company_name):
    subscription_user = request.subscription_user

    context={
        'subscription_user': subscription_user,  # Pass the subscription user details to the template
        'company_name':company_name,
    }

    return render(request,'hotel/privacy.html', context)

def terms_and_conditions(request,company_name):
    subscription_user = request.subscription_user

    context={
        'subscription_user': subscription_user,  # Pass the subscription user details to the template
        'company_name':company_name,
    }

    return render(request,'hotel/termsandconditions.html', context)

def cancellation(request,company_name):
    subscription_user = request.subscription_user

    context={
        'subscription_user': subscription_user,  # Pass the subscription user details to the template
        'company_name':company_name,
    }

    return render(request,'hotel/cancellation.html', context)

def fetch_room_types(request, company_name):
    subscription_user = request.subscription_user

    # Fetch room types associated with the subscription user
    room_types = RoomType.objects.filter(subscription_user=subscription_user).values('id', 'name')
    return JsonResponse(list(room_types), safe=False) 


def show_user_map(request):
    sub_user = SubscriptionUserDetails.objects.get(user=request.user)
    return render(request, "hotel/contact.html", {"embed_code": sub_user.map_embed_code})

