from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Room, Guest, Booking,TeamMember,FoodItem,RoomImage,CustomUser     
from .forms import RoomForm, GuestForm, BookingForm,TeamMemberForm,BulkRoomForm,FoodItemForm,VendorStaffRegistrationForm,LoginForm,ForgotPasswordForm,ResetPasswordForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.db.models import Q
from django.http import HttpResponse
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
import json
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .utils import CustomJSONEncoder
from django.db import models  # Add this import
from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import superuser_required
from django.http import FileResponse
from django.conf import settings
import os
from django.contrib.auth.models import User
from django.core.mail import send_mail
import uuid
from django.contrib.auth import get_user_model
from .signals import set_reset_token  # Adjust the import based on your project structure


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)
# Room Views
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'hotelapp/rooms1.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters from the request
        bed_type = self.request.GET.get('bed_type')
        seating_capacity = self.request.GET.get('seating_capacity')
        room_type = self.request.GET.get('room_type')

        # Filter by room type
        if room_type:
            queryset = queryset.filter(room_type=room_type)

        # Filter by bed type for non-conference rooms
        if room_type != 'conference' and bed_type:
            queryset = queryset.filter(bed_type=bed_type)

        # Filter by seating capacity for conference rooms
        if room_type == 'conference' and seating_capacity:
            queryset = queryset.filter(seating_capacity=seating_capacity)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['is_authenticated'] = self.request.user.is_authenticated
        context['is_admin'] = self.request.user.is_staff
        context['guest_id'] = self.request.GET.get('guest_id')
        context['check_in'] = self.request.GET.get('check_in')
        context['check_out'] = self.request.GET.get('check_out')
        return context

class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    template_name = 'hotelapp/room1.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch related images to optimize database queries
        context['room'] = Room.objects.prefetch_related('images').get(pk=self.object.pk)
        return context

# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_superuser

# Room Add View
@login_required
@superuser_required
def add_room(request):
    logger.info("Received a request to add a room.")
    form = RoomForm(addition_type=request.POST.get('additionType', None))
    bulk_form = BulkRoomForm()

    if request.method == 'POST':
        addition_type = request.POST.get('additionType')
        logger.info(f"Addition Type: {addition_type}")
        logger.info(f"POST Data: {request.POST}")

        # SINGLE ROOM ADDITION
        if addition_type == 'single':
            form = RoomForm(request.POST, request.FILES, addition_type='single')
            if form.is_valid():
                logger.info("Single Room Form is valid.")
                room = form.save(commit=False)
                room.features = request.POST.getlist('features')
                
                room.save()

                images = request.FILES.getlist('images')
                for image in images:
                    RoomImage.objects.create(room=room, image=image)
                messages.success(request, 'Room added successfully!')
                return redirect('admin-panel:room_list')
            else:
                logger.error(f"Single Room Form Errors: {form.errors}")
                messages.error(request, 'There were errors in your single room submission.')
                # import traceback
                # traceback.print_exc()
                # return render(request, 'hotelapp/addnewroomoffcanva.html', {
                #     'form': form,
                #     'bulk_form': bulk_form,
                # })

        # BULK ROOM ADDITION
        elif addition_type == 'bulk':
            bulk_form = BulkRoomForm(request.POST)
            form = RoomForm(addition_type='bulk')  # Prevent room_number validation

            logger.info("Validating Bulk Form...")
            if bulk_form.is_valid():
                logger.info("Bulk Form is valid.")
                logger.info(f"Bulk Form Data: {bulk_form.cleaned_data}")

                from_room = int(bulk_form.cleaned_data['from_room_number'])
                to_room = int(bulk_form.cleaned_data['to_room_number'])

                if from_room >= to_room:
                    logger.error(f"'To Room Number' ({to_room}) <= 'From Room Number' ({from_room})")
                    messages.error(request, "'To Room Number' must be greater than 'From Room Number'")
                    return render(request, 'hotelapp/rooms1.html', {
                        'form': form,
                        'bulk_form': bulk_form,
                    })

                # Bulk room creation
                for room_number in range(from_room, to_room + 1):
                    logger.info(f"Creating Room Number: {room_number}")
                    new_room = Room(
                        room_number=str(room_number),
                        block=request.POST.get('block'),
                        room_type=request.POST.get('room_type'),
                        bed_type=request.POST.get('bed_type'),
                        ac_type=request.POST.get('ac_type'),
                        base_price=request.POST.get('base_price'),
                        weekend_price=request.POST.get('weekend_price'),
                        holiday_price=request.POST.get('holiday_price'),
                        hourly_price=request.POST.get('hourly_price'),
                        max_occupancy=request.POST.get('max_occupancy'),
                        seating_capacity=request.POST.get('seating_capacity') if request.POST.get('room_type') == 'conference' else None,
                        features=request.POST.getlist('features'),
                        description=request.POST.get('description'),
                    )
                    new_room.save()

                    images = request.FILES.getlist('images')
                    for image in images:
                        RoomImage.objects.create(room=new_room, image=image)

                messages.success(request, f'{to_room - from_room + 1} rooms added successfully!')
                return redirect('admin-panel:room_list')
            else:
                logger.error(f"Bulk Form Errors: {bulk_form.errors}")
                logger.error(f"Room Form Errors: {form.errors}")
                messages.error(request, 'There were errors in your bulk room submission.')

    # Log and render errors if validation fails
    logger.info("Rendering errors if any...")
    logger.error(f"Room Form Errors: {form.errors}")
    logger.error(f"Bulk Form Errors: {bulk_form.errors}")

    return render(request, 'hotelapp/rooms1.html', {
        'form': form,
        'bulk_form': bulk_form,
        'form_errors': form.errors if request.method == 'POST' else None,
        'bulk_form_errors': bulk_form.errors if request.method == 'POST' else None,
    })

# Guest Views

@login_required
def guest_list(request):
    # Fetch all guests with their related bookings
    guests = Guest.objects.all().prefetch_related('booking_set')
    
    context = {
        'guests': guests,
    }
    return render(request, 'hotelapp/guest_list.html', context)
# def booking_list(request):
#     guests = Guest.objects.all().prefetch_related('booking_set')  # Fetch related bookings
#     return render(request, 'hotelapp/bookings.html', {
#         'guests': guests
#     })

class GuestListView(LoginRequiredMixin, ListView):
    model = Guest
    template_name = 'hotelapp/guest_list.html'
    context_object_name = 'guests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guest_id'] = self.request.GET.get('guest_id')
        return context

@login_required
def guest_create(request):
    room_id = request.GET.get('room')
    
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES)
        if form.is_valid():
            guest = form.save()
            messages.success(request, 'Guest registered successfully!')
            # Pass the room_id to booking creation if it exists
            if room_id:
                return redirect('admin-panel:bookings', guest_id=guest.id, room_id=room_id)
            return redirect('admin-panel:bookings', guest_id=guest.id)
    else:
        form = GuestForm()
    
    return render(request, 'hotelapp/guest_form.html', {
        'form': form,
        'room_id': room_id  # Pass room_id to template
    })

# Booking Views
# class BookingListView(ListView):
#     model = Booking
#     template_name = 'hotelapp/bookings.html'
#     context_object_name = 'bookings'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Convert datetime to string
#         context['now'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
#         # If you need to serialize bookings with datetime fields
#         bookings_data = []
#         for booking in context['bookings']:
#             booking_dict = {
#                 'id': booking.id,
#                 'check_in': booking.check_in.strftime('%Y-%m-%d %H:%M:%S') if booking.check_in else None,
#                 'check_out': booking.check_out.strftime('%Y-%m-%d %H:%M:%S') if booking.check_out else None,
#                 # Add other fields as needed
#             }
#             bookings_data.append(booking_dict)
        
#         context['bookings_data'] = bookings_data
#         return context

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'hotelapp/bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Get all bookings with related guest and room data
        queryset = Booking.objects.select_related('guest', 'room').all()
        
        # Optional: Add filters based on query parameters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Order by most recent first
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        
        # Add summary statistics
        context['total_bookings'] = self.get_queryset().count()
        context['total_amount'] = self.get_queryset().aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
        
        return context

def booking_detail(request, booking_id):
    
    booking =get_object_or_404(Booking.objects.select_related('guest', 'room'), id=booking_id)
    guest = booking.guest 
    context = {
        'guest': booking.guest,
        'room':booking.room,
        'booking': booking,
    }
    return render(request, 'hotelapp/bookingview1.html', context)


# class BookingDetailView(LoginRequiredMixin, DetailView):
#     model = Booking
#     template_name = 'hotelapp/booking-details.html'
#     context_object_name = 'booking'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Add any additional context here
#         return context

@require_POST
def check_room_availability(request):
    try:
        data = json.loads(request.body)
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room_type = data.get('room_type')
        bed_type = data.get('bed_type')
        ac_type = data.get('ac_type')

        # Convert check-in and check-out to datetime objects
        check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%dT%H:%M')
        check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%dT%H:%M')

        # Query to find available rooms
        available_rooms = Room.objects.filter(is_available=True).exclude(
            booking__check_in__lt=check_out_date,
            booking__check_out__gt=check_in_date
        )

        # Apply filters
        if room_type:
            available_rooms = available_rooms.filter(room_type=room_type)
        if bed_type:
            available_rooms = available_rooms.filter(bed_type=bed_type)
        if ac_type:
            available_rooms = available_rooms.filter(ac_type=ac_type)

        return JsonResponse({
            'success': True,
            'available_rooms': list(available_rooms.values('id', 'room_type', 'bed_type', 'ac_type', 'base_price'))
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# def booking_create(request):
#     room = None
#     room_type = None
#     bed_type = None
#     ac_type = None
#     seating_capacity = None

#     if request.method == 'POST':
#         # Check if a room was selected
#         room_id = request.POST.get('room_id')
#         if room_id:
#             try:
#                 room = Room.objects.get(pk=room_id)
#                 room_type = room.room_type
#                 bed_type = room.bed_type
#                 ac_type = room.ac_type
#                 seating_capacity = room.seating_capacity
#             except Room.DoesNotExist:
#                 messages.error(request, 'Selected room is not available.')
#                 return redirect('room_list')

#         # If no room was selected, get manual inputs
#         if not room:
#             room_type = request.POST.get('room_type')
#             bed_type = request.POST.get('bed_type')
#             ac_type = request.POST.get('ac_type')
#             seating_capacity = request.POST.get('seating_capacity')

#         # Process guest form
#         guest_form = GuestForm(request.POST)
#         if guest_form.is_valid():
#             guest = guest_form.save()

#             # Collect booking details
#             check_in = request.POST.get('check_in')
#             check_out = request.POST.get('check_out')
#             adults = request.POST.get('adults')
#             children = request.POST.get('children')
#             payment_type = request.POST.get('payment_type')

#             # Convert to timezone-aware datetime objects
#             try:
#                 check_in_date = make_aware(timezone.datetime.strptime(check_in, '%Y-%m-%dT%H:%M'))
#                 check_out_date = make_aware(timezone.datetime.strptime(check_out, '%Y-%m-%dT%H:%M'))
#             except ValueError:
#                 messages.error(request, 'Invalid date format.')
#                 return render(request, 'hotelapp/booking_form.html', {
#                     'guest_form': guest_form,
#                     'room': room,
#                     'room_type': room_type,
#                     'bed_type': bed_type,
#                     'ac_type': ac_type,
#                     'seating_capacity': seating_capacity,
#                 })

#             # Calculate total amount
#             if room:
#                 total_amount = room.room_price * max((check_out_date - check_in_date).days, 1)
#             else:
#                 # Logic to find a room based on manual inputs can be added here
#                 # For now, we will assume a default price for manual entries
#                 total_amount = 100.00 * max((check_out_date - check_in_date).days, 1)  # Example price

#             # Create booking
#             booking = Booking.objects.create(
#                 guest=guest,
#                 room=room,
#                 check_in=check_in_date,
#                 check_out=check_out_date,
#                 adults=adults,
#                 children=children,
#                 payment_type=payment_type,
#                 total_amount=total_amount,
#                 status='confirmed'
#             )
#             messages.success(request, 'Booking created successfully!')
#             return redirect('booking_detail', pk=booking.id)

#         else:
#             # If guest form is invalid, return with errors
#             return render(request, 'hotelapp/booking_form.html', {
#                 'guest_form': guest_form,
#                 'room': room,
#                 'room_type': room_type,
#                 'bed_type': bed_type,
#                 'ac_type': ac_type,
#                 'seating_capacity': seating_capacity,
#             })

#     # GET request handling
#     return render(request, 'hotelapp/booking_form.html', {
#         'guest_form': GuestForm(),
#         'room': room,
#         'room_type': room_type,
#         'bed_type': bed_type,
#         'ac_type': ac_type,
#         'seating_capacity': seating_capacity,
#     })

def booking_create(request):
    room = None
    room_type = request.GET.get('room_type')
    bed_type = request.GET.get('bed_type')
    ac_type = request.GET.get('ac_type')
    seating_capacity = request.GET.get('seating_capacity')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    # Check if a room is selected from the room list
    room_id = request.GET.get('room')
    if room_id:
        room = get_object_or_404(Room, pk=room_id)
        room_type = room.room_type
        bed_type = room.bed_type
        ac_type = room.ac_type
        seating_capacity = room.seating_capacity if room.room_type == 'conference' else None

    if request.method == 'POST':
        guest_form = GuestForm(request.POST, request.FILES)
        booking_form = BookingForm(request.POST)

        if guest_form.is_valid() and booking_form.is_valid():
            guest = guest_form.save(commit=False)

            # Handle proof type
            proof_type = request.POST.get('proof_type')  # Get the selected proof type
            guest.proof_type = proof_type  # Save the selected proof type

            # Get the proof number from the input field
            proof_number = request.POST.get('proof_no')
            if proof_type and not proof_number:
                # If a proof type is selected but no proof number is provided, raise an error
                guest.proof_no = None  # Set to None or handle as needed
                messages.error(request, "Proof number is required if proof type is selected.")
                return render(request, 'hotelapp/book.html', {
                    'guest_form': guest_form,
                    'booking_form': booking_form,
                    'room': room,
                })

            guest.proof_no = proof_number  # Save the proof number

            guest.save()

            booking = booking_form.save(commit=False)
            booking.guest = guest

            # Check if check-in time is greater than or equal to current time
            if booking.check_in < timezone.now():
                messages.error(request, 'Check-in time must be greater than or equal to the current time.')
                return render(request, 'hotelapp/book.html', {
                    'guest_form': guest_form,
                    'booking_form': booking_form,
                    'room': room,
                    'room_type': room_type,
                    'bed_type': bed_type,
                    'ac_type': ac_type,
                    'seating_capacity': seating_capacity,
                    'check_in': check_in,
                    'check_out': check_out,
                })

            # New validation: Check if check-out is greater than check-in
            if booking.check_out <= booking.check_in:
                messages.error(request, 'Check-out date must be greater than check-in date.')
                return render(request, 'hotelapp/book.html', {
                    'guest_form': guest_form,
                    'booking_form': booking_form,
                    'room': room,
                    'room_type': room_type,
                    'bed_type': bed_type,
                    'ac_type': ac_type,
                    'seating_capacity': seating_capacity,
                    'check_in': check_in,
                    'check_out': check_out,
                })

            # If a room was selected from the list
            if room:
                # Check if the room is already booked for the selected dates
                existing_bookings = Booking.objects.filter(
                    room=room,
                    check_out__gt=booking.check_in,
                    check_in__lt=booking.check_out
                )
                if existing_bookings.exists():
                    messages.error(request, f'Room {room.room_number} is already booked for the selected dates.')
                    return render(request, 'hotelapp/book.html', {
                        'guest_form': guest_form,
                        'booking_form': booking_form,
                        'room': room,
                        'room_type': room_type,
                        'bed_type': bed_type,
                        'ac_type': ac_type,
                        'seating_capacity': seating_capacity,
                        'check_in': check_in,
                        'check_out': check_out,
                    })
                booking.room = room
            else:
                # Handle direct booking (manual room selection)
                room_type = request.POST.get('room_type')
                bed_type = request.POST.get('bed_type')
                ac_type = request.POST.get('ac_type')
                seating_capacity = request.POST.get('seating_capacity')

                # Find an available room based on the criteria
                available_rooms = Room.objects.filter(
                    room_type=room_type,
                    bed_type=bed_type if room_type != 'conference' else 'none',
                    seating_capacity=seating_capacity if room_type == 'conference' else None,
                    ac_type=ac_type,
                    is_available=True
                ).exclude(
                    booking__check_out__gt=booking.check_in,
                    booking__check_in__lt=booking.check_out
                )
                if available_rooms.exists():
                    booking.room = available_rooms.first()
                else:
                    messages.error(request, 'No rooms available matching your criteria.')
                    return render(request, 'hotelapp/book.html', {
                        'guest_form': guest_form,
                        'booking_form': booking_form,
                        'room': room,
                        'room_type': room_type,
                        'bed_type': bed_type,
                        'ac_type': ac_type,
                        'seating_capacity': seating_capacity,
                        'check_in': check_in,
                        'check_out': check_out,
                    })

            # Calculate total amount (implement your pricing logic here)
            nights = (booking.check_out - booking.check_in).days
            booking.total_amount = booking.room.room_price * max(nights, 1)

            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('admin-panel:booking_detail', pk=booking.pk)
        else:
            # Add this block to handle form errors
            print(guest_form.errors)  # For debugging
            print(booking_form.errors)  # For debugging
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_data = {}
        if check_in and check_out:
            try:
                initial_data['check_in'] = datetime.strptime(check_in, '%Y-%m-%d %H:%M')
                initial_data['check_out'] = datetime.strptime(check_out, '%Y-%m-%d %H:%M')
            except ValueError:
                try:
                    initial_data['check_in'] = datetime.strptime(check_in, '%Y-%m-%dT%H:%M')
                    initial_data['check_out'] = datetime.strptime(check_out, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass
        guest_form = GuestForm()
        booking_form = BookingForm(initial=initial_data)

    return render(request, 'hotelapp/book.html', {
        'guest_form': guest_form,
        'booking_form': booking_form,
        'room': room,
        'room_type': room_type,
        'bed_type': bed_type,
        'ac_type': ac_type,
        'seating_capacity': seating_capacity,
        'check_in': check_in,
        'check_out': check_out,
    })

def calculate_total_amount(room, check_in, check_out):
    # Implement your pricing logic here
    nights = (check_out - check_in).days
    return room.room_price * max(nights, 1)

def guest_booking_create(request):
    # Get parameters from URL
    guest_id = request.GET.get('guest_id')
    room_id = request.GET.get('room')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not guest_id or not room_id:
        messages.error(request, 'Missing guest or room information')
        return redirect('admin-panel:room_list')
    
    # Get guest and room objects
    try:
        guest = Guest.objects.get(pk=guest_id)
        room = Room.objects.get(pk=room_id)
    except (Guest.DoesNotExist, Room.DoesNotExist):
        messages.error(request, 'Guest or Room not found')
        return redirect('admin-panel:room_list')
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        
        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.guest = guest
            booking.room = room
            
            # Validate booking dates
            if booking.check_in < timezone.now():
                messages.error(request, 'Check-in time must be greater than or equal to the current time.')
                return render(request, 'hotelapp/guest_booking_form.html', {
                    'booking_form': booking_form,
                    'guest': guest,
                    'room': room,
                })
            
            if booking.check_out <= booking.check_in:
                messages.error(request, 'Check-out date must be greater than check-in date.')
                return render(request, 'hotelapp/guest_booking_form.html', {
                    'booking_form': booking_form,
                    'guest': guest,
                    'room': room,
                })
            
            # Calculate total amount
            nights = (booking.check_out - booking.check_in).days
            booking.total_amount = room.base_price * max(nights, 1)
            
            booking.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('admin-panel:booking_detail', pk=booking.pk)
    else:
        # Pre-fill the form with check-in and check-out dates if provided
        initial_data = {}
        if check_in and check_out:
            try:
                # Try different format patterns
                try:
                    initial_data['check_in'] = datetime.strptime(check_in, '%Y-%m-%d %H:%M')
                    initial_data['check_out'] = datetime.strptime(check_out, '%Y-%m-%d %H:%M')
                except ValueError:
                    try:
                        initial_data['check_in'] = datetime.strptime(check_in, '%Y-%m-%dT%H:%M')
                        initial_data['check_out'] = datetime.strptime(check_out, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        print(f"Could not parse dates: check_in={check_in}, check_out={check_out}")
            except Exception as e:
                print(f"Error processing dates: {e}")
                
        booking_form = BookingForm(initial=initial_data)
    
    # Always render the guest booking form template
    return render(request, 'hotelapp/guest_booking_form.html', {
        'booking_form': booking_form,
        'guest': guest,
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
    })

# Team Add View
@login_required
@superuser_required
def add_team_member(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()  # Save the form data to the database
                messages.success(request, 'Team member added successfully!')
                return redirect('admin-panel:team_list')  # Redirect to the team add page or another page
            except IntegrityError:
                form.add_error(None, "A team member with these details already exists.")
        else:
            # If the form is not valid, we'll render it again with errors
            print("Form errors:", form.errors)  # Debugging line
    else:
        form = TeamMemberForm()
    
    return render(request, 'hotelapp/team-add.html', {'form': form})


def team_list(request):
    query = request.GET.get('search', '')  # Get the search query from the GET request
    if query:
        team_members = TeamMember.objects.filter(name__icontains=query).order_by('name')  # Filter by name
    else:
        team_members = TeamMember.objects.all().order_by('name')  # Get all members if no query

    return render(request, 'hotelapp/team-list.html', {
        'team_members': team_members
    })

@require_http_methods(["GET", "POST"])
def edit_team_member(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            form.save()  # Save the updated form data to the database
            messages.success(request, 'Team member updated successfully!')
            return redirect('admin-panel:team_list')  # Redirect to the team list page
        else:
            print("Form errors:", form.errors)  # Debugging line
    else:
        form = TeamMemberForm(instance=team_member)
    
    return render(request, 'hotelapp/team-edit.html', {'form': form, 'team_member': team_member, 'member': team_member})

@require_http_methods(["GET", "POST"])
def delete_team_member(request, member_id):
    team_member = get_object_or_404(TeamMember, id=member_id)
    if request.method == 'POST':
        team_member.delete()  # Delete the team member
        messages.success(request, 'Team member deleted successfully!')
        return redirect('admin-panel:team_list')  # Redirect to the team list page
    return render(request, 'hotelapp/team-delete.html', {'team_member': team_member})

def invoice_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/invoice.html', context)


def menu_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/menu.html', context)
@login_required
@superuser_required
def menu_add_view(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added successfully!')
            return redirect('admin-panel:menu')
        else:
            messages.error(request, 'There was an error adding the food item.')
    else:
        form = FoodItemForm()
    
    return render(request, 'hotelapp/menu.html', {'form': form})

def orders_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/orders.html', context)

def forgot_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/forgot.html', context)

def reset_password_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/reset-password.html', context)
def register(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')  # Updated from uname
        email = request.POST.get('email')
        password = request.POST.get('password')  # Updated from psw
        password2 = request.POST.get('password2')  # Get password confirmation
        user_type = request.POST.get('user_type')

        # Print form data for debugging
        print("Form data received:", {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'user_type': user_type
        })

        # Validate required fields
        if not all([first_name, last_name, username, email, password, password2, user_type]):
            messages.error(request, 'All fields are required.')
            return render(request, 'hotelapp/signup.html')

        # Check if passwords match
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'hotelapp/signup.html')

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'hotelapp/signup.html')

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'hotelapp/signup.html')

        try:
            # Create new user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('admin-panel:login')

        except Exception as e:
            print(f"Error creating user: {str(e)}")  # Debug print
            messages.error(request, f'An error occurred during registration. Please try again.')
            return render(request, 'hotelapp/signup.html')

    return render(request, 'hotelapp/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin-panel:index')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'admin-panel:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'hotelapp/login.html', {
        'form': form,
        'page_type': 'login'
    })

@login_required
def logout_view(request):
    if request.method == 'POST':  # Only allow POST requests for logout
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('admin-panel:login')
    return redirect('admin-panel:index')  # Redirect to index if not POST



def custom_404_view(request, exception):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/404-error-page.html', context, status=404)


@login_required
def index_view(request):
    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
        # Add any other context data you need
    }
    return render(request, 'hotelapp/index.html', context)


# def signup_view(request):
#     # You can add any context data you want to pass to the template here
#     context = {}
#     return render(request, 'hotelapp/signup.html', context)


def role_view(request):
    # You can add any context data you want to pass to the template here
    context = {}
    return render(request, 'hotelapp/role.html', context)



def multiple_bookings_create(request):
    if request.method == 'POST':
        try:
            # Create a mutable copy of POST data
            post_data = request.POST.copy()
           
            proof_type = request.POST.get('proof_type')
            proof_no = request.POST.get('proof_no')
            
            print("Proof Type:", proof_type)  # Debug print
            print("Proof Number:", proof_no)   # Debug print

            print("POST data:", post_data)  # Debug logging
            print("FILES:", request.FILES)  # Debug logging
            print("Proof Type:", proof_type)  # Debug print


            # Safely retrieve proof_type
            if not proof_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Please select an ID proof type'
                })
            # Log proof_type safely
            #print("Proof Type:", proof_type)

            guest_form = GuestForm(post_data, request.FILES)
            booking_form = BookingForm(post_data)

            guest_form.data = guest_form.data.copy()
            guest_form.data['proof_type'] = proof_type

            if not guest_form.is_valid():
                print("Guest Form Errors:", guest_form.errors)  # Debug logging
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid guest information',
                    'errors': guest_form.errors
                })

            if not booking_form.is_valid():
                print("Booking Form Errors:", booking_form.errors)  # Debug logging
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid booking information',
                    'errors': booking_form.errors
                })

            # Validate check-in and check-out dates
            check_in = booking_form.cleaned_data['check_in']
            check_out = booking_form.cleaned_data['check_out']
            if timezone.is_naive(check_in):
                check_in = timezone.make_aware(check_in)
            if timezone.is_naive(check_out):
                check_out = timezone.make_aware(check_out)

            if check_in < timezone.now():
                return JsonResponse({
                    'success': False,
                    'error': 'Check-in time cannot be in the past.'
                })

            if check_out <= check_in:
                return JsonResponse({
                    'success': False,
                    'error': 'Check-out time must be after check-in time.'
                })

            # Process selected rooms
            selected_rooms = json.loads(post_data.get('selectedRooms', '[]'))
            if not selected_rooms:
                return JsonResponse({
                    'success': False,
                    'error': 'Room selection is required.'
                })

            proof_no = post_data.get('proof_no')
            if not proof_no:
                return JsonResponse({
                    'success': False,
                    'error': 'Proof number is required.'
                })
            if 'proof_type' not in request.POST:
                print("Error: proof_type missing in POST data.")

            # Begin transaction
            with transaction.atomic():
                guest = guest_form.save(commit=False)
                guest.proof_type = proof_type
                guest.proof_no = proof_no
                guest.save()

                total_amount = 0
                bookings = []

                for room_data in selected_rooms:
                    room_type = room_data['roomType']
                    bed_type = room_data.get('bedType')
                    ac_type = room_data.get('acType')
                    room_count = int(room_data.get('roomCount', 1))
                    seating_capacity = room_data.get('sittingCapacity')

                    # Build query for available rooms
                    query = Q(room_type=room_type, ac_type=ac_type, is_available=True)
                    if room_type != 'conference':
                        query &= Q(bed_type=bed_type)
                    else:
                        query &= Q(seating_capacity=seating_capacity)

                    available_rooms = Room.objects.filter(query).exclude(
                        booking__check_out__gt=check_in,
                        booking__check_in__lt=check_out
                    )

                    available_count = available_rooms.count()
                    if available_count < room_count:
                        raise ValidationError(
                            f'Only {available_count} {room_type} rooms available with '
                            f'{"bed type " + bed_type if bed_type else ""} '
                            f'and AC type {ac_type} for the selected dates. '
                            f'You requested {room_count} rooms.'
                        )

                    selected_rooms = available_rooms[:room_count]
                    nights = max((check_out - check_in).days, 1)

                    for room in selected_rooms:
                        booking = Booking(
                            guest=guest,
                            room=room,
                            check_in=check_in,
                            check_out=check_out,
                            adults=booking_form.cleaned_data['adults'],
                            children=booking_form.cleaned_data['children'],
                            payment_type=booking_form.cleaned_data['payment_type'],
                            total_amount=room.base_price * nights
                        )
                        bookings.append(booking)
                        total_amount += booking.total_amount

                Booking.objects.bulk_create(bookings)
                guest.total_amount = total_amount
                guest.save()

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('admin-panel:booking_list'),
                'message': f'Successfully booked {len(bookings)} room(s).'
            })

        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            })
    else:  # Handle GET request
        guest_form = GuestForm()
        booking_form = BookingForm()
        return render(request, 'hotelapp/bookings.html', {
            'guest_form': guest_form,
            'booking_form': booking_form,
        })

@require_POST
def get_room_price(request):
    try:
        data = json.loads(request.body)
        room_type = data.get('room_type')
        bed_type = data.get('bed_type')
        ac_type = data.get('ac_type')
        sitting_capacity = data.get('sitting_capacity')
        check_in = data.get('check_in')  # Get check-in date
        check_out = data.get('check_out')  # Get check-out date

        # Convert ac_type from frontend format to database format
        if ac_type == 'nonAc':
            ac_type = 'nonAc'

        # Query to find available rooms
        available_rooms = Room.objects.filter(is_available=True)

        # Apply filters
        if room_type:
            available_rooms = available_rooms.filter(room_type=room_type)
        if bed_type:
            available_rooms = available_rooms.filter(bed_type=bed_type)
        if ac_type:
            available_rooms = available_rooms.filter(ac_type=ac_type)
        if sitting_capacity and room_type == 'conference':
            available_rooms = available_rooms.filter(seating_capacity=sitting_capacity)

        # If check-in and check-out are provided, filter based on bookings
        if check_in and check_out:
            try:
                check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%dT%H:%M')
                check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%dT%H:%M')
                
                # Make dates timezone aware
                if timezone.is_naive(check_in_date):
                    check_in_date = timezone.make_aware(check_in_date)
                if timezone.is_naive(check_out_date):
                    check_out_date = timezone.make_aware(check_out_date)

                # Exclude rooms that have bookings overlapping with the requested period
                booked_rooms = Booking.objects.filter(
                    check_in__lt=check_out_date,
                    check_out__gt=check_in_date
                ).values_list('room_id', flat=True)
                
                available_rooms = available_rooms.exclude(id__in=booked_rooms)
            except ValueError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid date format: {str(e)}'
                })

        # Get the count of available rooms
        available_count = available_rooms.count()

        return JsonResponse({
            'success': True,
            'price': float(available_rooms.first().base_price) if available_count > 0 else 0,
            'available': available_count
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST, instance=booking)
        guest_form = GuestForm(request.POST, request.FILES, instance=booking.guest)
        
        if booking_form.is_valid() and guest_form.is_valid():
            try:
                with transaction.atomic():
                    # Save guest info
                    guest = guest_form.save()
                    
                    # Save booking info
                    booking = booking_form.save(commit=False)
                    booking.guest = guest
                    
                    # Validate dates
                    if booking.check_out <= booking.check_in:
                        messages.error(request, 'Check-out date must be after check-in date.')
                        return render(request, 'hotelapp/edit_booking.html', {
                            'booking_form': booking_form,
                            'guest_form': guest_form,
                            'booking': booking
                        })
                    
                    # Check room availability (excluding current booking)
                    conflicting_bookings = Booking.objects.filter(
                        room=booking.room,
                        check_out__gt=booking.check_in,
                        check_in__lt=booking.check_out
                    ).exclude(id=booking_id)
                    
                    if conflicting_bookings.exists():
                        messages.error(request, 'Room is not available for selected dates.')
                        return render(request, 'hotelapp/edit_booking.html', {
                            'booking_form': booking_form,
                            'guest_form': guest_form,
                            'booking': booking
                        })
                    
                    # Calculate total amount
                    nights = (booking.check_out - booking.check_in).days
                    booking.total_amount = booking.room.base_price * max(nights, 1)
                    
                    booking.save()
                    messages.success(request, 'Booking updated successfully!')
                    return redirect('admin-panel:booking_list')
                    
            except Exception as e:
                messages.error(request, f'Error updating booking: {str(e)}')
                
    else:
        booking_form = BookingForm(instance=booking)
        guest_form = GuestForm(instance=booking.guest)
    
    return render(request, 'hotelapp/edit_booking.html', {
        'booking_form': booking_form,
        'guest_form': guest_form,
        'booking': booking
    })

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Store guest reference
                guest = booking.guest
                
                # Delete booking
                booking.delete()
                
                # Check if guest has other bookings
                if not guest.booking_set.exists():
                    # If guest has no other bookings, delete guest too
                    guest.delete()
                
                messages.success(request, 'Booking deleted successfully!')
                return redirect('admin-panel:booking_list')
                
        except Exception as e:
            messages.error(request, f'Error deleting booking: {str(e)}')
            return redirect('admin-panel:booking_list')
    
    return render(request, 'hotelapp/delete_booking.html', {
        'booking': booking
    })
                
#                 if booking.check_out <= booking.check_in:
#                     messages.error(request, 'Check-out date must be greater than check-in date.')
#                     return render(request, 'hotelapp/guest_booking_form.html', {
#                         'booking_form': booking_form,
#                         'guest': guest,
#                         'room': room,
#                     })
                
#                 # Calculate total amount
#                 nights = (booking.check_out - booking.check_in).days
#                 booking.total_amount = room.room_price * max(nights, 1)
                
#                 booking.save()
#                 messages.success(request, 'Booking created successfully!')
#                 return redirect('booking_detail', pk=booking.pk)
    
#     else:
#         # Handle GET request
#         guest_form = GuestForm()
#         booking_form = BookingForm()

#     return render(request, 'hotelapp/multiple_bookings.html', {
#         'guest_form': guest_form,
#         'booking_form': booking_form,
#     })

@login_required
@superuser_required
def add_food_item(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added successfully!')
            return redirect('admin-panel:menu')
        else:
            messages.error(request, 'There was an error adding the food item.')
    else:
        form = FoodItemForm()
    
    return render(request, 'hotelapp/menu.html', {'form': form})

def menu_view(request):
    breakfast_items = FoodItem.objects.filter(category='breakfast')
    lunch_items = FoodItem.objects.filter(category='lunch')
    dinner_items = FoodItem.objects.filter(category='dinner')
    
    return render(request, 'hotelapp/menu.html', {
        'breakfast_items': breakfast_items,
        'lunch_items': lunch_items,
        'dinner_items': dinner_items,
    })

def lunch_section(request):
    lunch_items = FoodItem.objects.filter(category='lunch')  # Fetch lunch items
    return render(request, 'hotelapp/lunchsection.html', {'lunch_items': lunch_items})

def dinner_section(request):
    dinner_items = FoodItem.objects.filter(category='dinner')  # Fetch dinner items
    return render(request, 'hotelapp/dinnersection.html', {'dinner_items': dinner_items})


def breakfast_section(request):
    breakfast_items = FoodItem.objects.filter(category='breakfast')  # Fetch breakfast items
    return render(request, 'hotelapp/breakfastsection.html', {'breakfast_items': breakfast_items})

@login_required
def view_document(request, doc_type, member_id):
    """View for handling document downloads/viewing"""
    team_member = get_object_or_404(TeamMember, id=member_id)
    
    if doc_type == 'aadhar':
        if team_member.aadhar_file:
            file_path = team_member.aadhar_file.path
            filename = os.path.basename(file_path)
    elif doc_type == 'pan':
        if team_member.pan_file:
            file_path = team_member.pan_file.path
            filename = os.path.basename(file_path)
    else:
        messages.error(request, 'Invalid document type')
        return redirect('admin-panel:team_list')
    
    try:
        response = FileResponse(open(file_path, 'rb'))
        # Set content type based on file extension
        if filename.endswith('.pdf'):
            response['Content-Type'] = 'application/pdf'
        elif filename.endswith(('.jpg', '.jpeg')):
            response['Content-Type'] = 'image/jpeg'
        elif filename.endswith('.png'):
            response['Content-Type'] = 'image/png'
        
        # Set to display in browser rather than download
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except FileNotFoundError:
        messages.error(request, 'File not found')
        return redirect('admin-panel:team_list')

@login_required
@superuser_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        try:
            # Update room data
            room.room_number = request.POST.get('room_number')
            room.block = request.POST.get('block')
            room.room_type = request.POST.get('room_type')
            room.bed_type = request.POST.get('bed_type')
            room.ac_type = request.POST.get('ac_type')
            room.base_price = request.POST.get('base_price')
            room.max_occupancy = request.POST.get('max_occupancy')
            room.description = request.POST.get('description')
            
            # Handle images
            if request.FILES.getlist('images'):
                # Delete old images
                room.images.all().delete()
                # Add new images
                for image in request.FILES.getlist('images'):
                    RoomImage.objects.create(room=room, image=image)
            
            room.save()
            messages.success(request, 'Room updated successfully!')
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # For GET request, return room data
    data = {
        'id': room.id,
        'room_number': room.room_number,
        'block': room.block,
        'room_type': room.room_type,
        'bed_type': room.bed_type,
        'ac_type': room.ac_type,
        'base_price': str(room.base_price),
        'max_occupancy': room.max_occupancy,
        'description': room.description,
    }
    return JsonResponse(data)

@login_required
@superuser_required
def delete_room(request, room_id):
    if request.method == 'POST':
        try:
            room = get_object_or_404(Room, id=room_id)
            room.delete()
            messages.success(request, 'Room deleted successfully!')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# @login_required
# def RoomDetailView(request, guest_id):
#     guest = get_object_or_404(Guest, id=guest_id)
#     bookings = guest.booking_set.all()
    
#     context = {
#         'guest': guest,
#         'bookings': bookings,
#     }
#     return render(request, 'hotelapp/guest-details.html', context)

@login_required
def delete_guest(request, guest_id):
    if request.method == 'POST':
        guest = get_object_or_404(Guest, id=guest_id)
        try:
            guest.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def guest_detail(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    bookings = guest.booking_set.all()
    
    context = {
        'guest': guest,
        'bookings': bookings,
    }
    return render(request, 'hotelapp/guest-details.html', context)


def check_availability(request):
    available_rooms = None  # Initialize available_rooms

    if request.method == 'POST':
        check_in_date = request.POST.get('check_in')
        check_out_date = request.POST.get('check_out')
        room_type = request.POST.get('room_type')

        # Convert to datetime objects
        check_in_date = timezone.datetime.strptime(check_in_date, '%Y-%m-%dT%H:%M')
        check_out_date = timezone.datetime.strptime(check_out_date, '%Y-%m-%dT%H:%M')

        # Query to find available rooms based on filters
        available_rooms = Room.objects.filter(is_available=True).exclude(
            booking__check_in__lt=check_out_date,
            booking__check_out__gt=check_in_date
        )

        # Apply room type filter if selected
        if room_type:
            available_rooms = available_rooms.filter(room_type=room_type)

    return render(request, 'hotelapp/rooms1.html', {
        'available_rooms': available_rooms,  # Pass available rooms if any
        'check_in': check_in_date if request.method == 'POST' else None,
        'check_out': check_out_date if request.method == 'POST' else None,
        'room_type': room_type,
    })

# View for Forgot Password
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            set_reset_token(user)  # Call the function to set the token and timestamp

            reset_link = request.build_absolute_uri(reverse('admin-panel:reset_password', args=[user.profile.reset_token]))
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, "A link to reset your password has been sent to your email.")
            return redirect('admin-panel:login')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
    return render(request, 'hotelapp/forgot.html')

# View for Reset Password
def reset_password(request, token):
    User = get_user_model()
    try:
        user = User.objects.get(profile__reset_token=token)
        profile = user.profile

        # Check if the token is still valid (10 minutes)
        if profile.reset_token_created_at < timezone.now() - timedelta(minutes=10):
            messages.error(request, "This reset link has expired. Please request a new one.")
            return redirect('admin-panel:forgot_password')
    except User.DoesNotExist:
        messages.error(request, "Invalid or expired token.")
        return redirect('admin-panel:forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password').strip()
        confirm_password = request.POST.get('confirm_password').strip()

        if password == confirm_password:
            user.set_password(password)
            profile.reset_token = ''
            profile.reset_token_created_at = None  # Clear the timestamp
            profile.save()
            user.save()
            messages.success(request, "Your password has been reset successfully. You can now log in with your new password.")
            return redirect('admin-panel:login')
        else:
            messages.error(request, "Passwords do not match. Please try again.")
    return render(request, 'hotelapp/reset-password.html')



