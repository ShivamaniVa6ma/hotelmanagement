from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib import messages
from hotelapp.models import Room, Booking,Guest
from hotelapp.forms import RoomForm,BulkRoomForm, BookingForm,GuestForm,RoomSelectionForm
from datetime import datetime
import json
from decimal import Decimal
from django.db.models import Q
import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse

logger = logging.getLogger(__name__)

@require_POST
def check_availability(request):
    check_in = request.POST.get('check_in')
    check_out = request.POST.get('check_out')
    room_type = request.POST.get('room_type')
    
    if check_in and check_out:
        try:
            # Parse the incoming date strings
            check_in = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
            check_out = datetime.strptime(check_out, "%Y-%m-%dT%H:%M")

            # Ensure the dates are timezone-aware
            check_in = timezone.make_aware(check_in)
            check_out = timezone.make_aware(check_out)

            available_rooms = Room.objects.filter(
                room_type=room_type,
                is_available=True
            ).exclude(
                booking__check_in__lt=check_out,
                booking__check_out__gt=check_in
            )
            
            return render(request, 'hotel/checkout.html', {
                'available_rooms': available_rooms,
                'check_in': check_in,
                'check_out': check_out
            })
        except ValueError as e:
            return JsonResponse({'error': 'Invalid date format. Please use the correct format.'}, status=400)

    return redirect('user-panel:index')



@require_POST
@transaction.atomic
def create_booking(request):
    guest_form = GuestForm(request.POST, request.FILES)
    booking_form = BookingForm(request.POST)

    logger.info("Received booking request")

    if guest_form.is_valid() and booking_form.is_valid():
        try:
            guest = guest_form.save()
            booking = booking_form.save(commit=False)
            booking.guest = guest

            selected_rooms = json.loads(request.POST.get('selectedRooms', '[]'))
            logger.info(f"Selected rooms: {selected_rooms}")
            
            if not selected_rooms:
                logger.warning("No rooms selected")
                return JsonResponse({'error': 'No rooms selected'}, status=400)

            bookings = []
            
            for room_data in selected_rooms:
                room_id = room_data['id']
                room = Room.objects.select_for_update().get(id=room_id)
                
                if not room.is_available:
                    logger.warning(f"Room {room.room_number} is not available")
                    raise ValueError(f'Room {room.room_number} is no longer available.')

                new_booking = Booking(
                    guest=guest,
                    room=room,
                    check_in=booking.check_in,
                    check_out=booking.check_out,
                    adults=booking.adults,
                    children=booking.children,
                    payment_type=booking.payment_type,
                    total_amount=room.base_price
                )
                bookings.append(new_booking)
                room.is_available = False
                room.save()

            created_bookings = Booking.objects.bulk_create(bookings)
            logger.info(f"Created {len(created_bookings)} bookings successfully")

            # Get the ID of the first booking (assuming all bookings are for the same guest)
            first_booking_id = created_bookings[0].id if created_bookings else None

            success_url = reverse('user-panel:booking_success') + f'?booking_id={first_booking_id}'
            return JsonResponse({'success': True, 'redirect_url': success_url})
        except ValueError as e:
            logger.error(f"ValueError in create_booking: {str(e)}")
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in create_booking: {str(e)}")
            transaction.set_rollback(True)
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    else:
        errors = {}
        if not guest_form.is_valid():
            errors['guest_form'] = guest_form.errors
        if not booking_form.is_valid():
            errors['booking_form'] = booking_form.errors
        logger.error(f"Form validation errors: {errors}")
        return JsonResponse({'error': 'Invalid form data', 'errors': errors}, status=400)

def booking_success(request):
        booking_id = request.GET.get('booking_id')
        return render(request, 'hotel/booking_success.html', {'booking_id': booking_id})

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

def index(request):
    # Render the index.html template
    return render(request, 'hotel/index.html')

def about(request):
    # Render the about.html template
    return render(request, 'hotel/about.html')

def contact(request):
    # Render the contact.html template
    return render(request, 'hotel/contact.html')

def room(request):
    # Render the room.html template
    return render(request, 'hotel/room.html')

def booking(request):
    # Render the booking.html template
    return render(request, 'hotel/booking.html')

def team(request):
    # Render the team.html template
    return render(request, 'hotel/team.html')

def facilities(request):
    # Render the facilities.html template
    return render(request, 'hotel/facilities.html')


def frequently_asked_questions(request):
    # Render the frequently_asked_questions.html template
    return render(request, 'hotel/faq.html')

def services(request):
    # Render the services.html template
    return render(request, 'hotel/services.html')

def spa(request):
    # Render the spa.html template
    return render(request, 'hotel/spa.html')

def checkout(request):
    # Render the checkout.html template
    return render(request, 'hotel/checkout.html')


def room_details(request):
    # Render the room_details.html template
    return render(request, 'hotel/room-details.html')

def room_two(request):
    # Render the room_two.html template
    return render(request, 'hotel/room-2.html')

def gallery(request):
    # Render the gallery.html template
    return render(request, 'hotel/gallery.html')

def restaurant(request):
    # Render the restaurant.html template
    return render(request, 'hotel/restaurant.html')

def contact_us(request):
    # Render the contact_us.html template
    return render(request, 'hotel/contact.html')

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

def fetch_rooms(request):
    if request.method == 'GET':
        room_types = request.GET.getlist('room_type[]')
        bed_type = request.GET.get('bed_type')
        seating_capacity = request.GET.get('seating_capacity')

        # Base query
        rooms_query = Room.objects.filter(room_type__in=room_types)

        # Filter by bed type if provided and not conference room
        if bed_type and 'conference' not in room_types:
            rooms_query = rooms_query.filter(bed_type=bed_type)

        # Filter by seating capacity for conference rooms
        if seating_capacity and 'conference' in room_types:
            rooms_query = rooms_query.filter(seating_capacity=seating_capacity)

        # Fetch matching rooms
        rooms = rooms_query.values('id', 'room_number', 'room_type', 'ac_type', 'is_available', 'seating_capacity')

        # Organize rooms by type and attribute
        response_data = {}
        for room_type in room_types:
            response_data[room_type] = {
                'ac': [],
                'nonAc': []
            }
            type_rooms = [r for r in rooms if r['room_type'] == room_type]
            for room in type_rooms:
                room_data = {
                    'id': room['id'],
                    'room_number': room['room_number'],
                    'is_available': room['is_available']
                }
                if room_type == 'conference':
                    room_data['seating_capacity'] = room['seating_capacity']

                if room['ac_type'] == 'ac':
                    response_data[room_type]['ac'].append(room_data)
                else:
                    response_data[room_type]['nonAc'].append(room_data)

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

