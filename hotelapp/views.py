from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Room, Guest, Booking,TeamMember,FoodItem,RoomImage,CustomUser, RoomType, LogoSettings,TeamDesignation,Event,Feature,Facility, FAQ, Spa, AboutUs, Service,ContactMessage,Tax as HotelTax
from .forms import RoomForm, GuestForm, BookingForm,TaxForm,TeamMemberForm,BulkRoomForm,FoodItemForm,LoginForm,ForgotPasswordForm,ResetPasswordForm, RoomTypeForm, LogoSettingsForm,TeamDesignationForm,EventForm,FeatureForm, FacilityForm,AboutUsForm,GuestOTPForm
from django.views.generic import ListView, DetailView, TemplateView
from hotel.models import UserMap
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
import json
from django.db.models.functions import TruncDate
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from io import BytesIO
import random
from django.core.mail import EmailMessage
from decimal import Decimal, ROUND_HALF_UP
from django.utils.dateparse import parse_date
# from django.utils.timesince import timesince
from django.contrib.humanize.templatetags.humanize import naturaltime
from calendar import month_name
from django.utils.timezone import now
from hotelapp.utils import generate_invoice_id

from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
from django.http import JsonResponse, HttpResponse,HttpResponseBadRequest
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
from subscription.models import SubscriptionUserDetails, Cart, SubscriptionPlan,Tax as SubscriptionTax
from .mixins import SubscriptionRequiredMixin
from django.views import View
from collections import defaultdict
from django.utils.dateparse import parse_datetime
from django.db.models import Count, Sum,Prefetch


from django.views.decorators.http import require_POST,require_GET
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)


# Room Views
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'hotelapp/rooms1.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        self.check_in = self.request.GET.get('check_in')
        self.check_out = self.request.GET.get('check_out')
        self.room_type = self.request.GET.get('room_type')
        self.bed_type = self.request.GET.get('bed_type')
        self.seating_capacity = self.request.GET.get('seating_capacity')
        self.ac_type = self.request.GET.get('ac_type')

        print(f"Form values - check_in: {self.check_in}, check_out: {self.check_out}")
        print(f"Current user: {self.request.user}")

        subscription_user = SubscriptionUserDetails.objects.filter(
            user=self.request.user, 
            is_active=True
        ).first()

        print(f"Subscription user found: {subscription_user}")

        if not subscription_user:
            print("No active subscription found for user")
            return Room.objects.none()

        # Get all rooms for the subscription user (without availability filter)
        queryset = Room.objects.filter(
            subscription_user=subscription_user
        ).select_related('room_type').prefetch_related('images')

        print(f"Initial queryset count: {queryset.count()}")
        print(f"Room numbers: {list(queryset.values_list('room_number', flat=True))}")

        # Filter mode: check_in + check_out available → filter by form
        if self.check_in and self.check_out:
            try:
                check_in_date = timezone.make_aware(
                    timezone.datetime.strptime(self.check_in, '%Y-%m-%dT%H:%M')
                )
                check_out_date = timezone.make_aware(
                    timezone.datetime.strptime(self.check_out, '%Y-%m-%dT%H:%M')
                )
                
                print(f"Parsed dates - check_in: {check_in_date}, check_out: {check_out_date}")
                
                # Exclude rooms that are booked in the given time frame
                queryset = queryset.exclude(
                    bookings__check_in__lt=check_out_date,
                    bookings__check_out__gt=check_in_date
                ).distinct()

                print(f"After availability filter count: {queryset.count()}")
                print(f"Available room numbers after booking filter: {list(queryset.values_list('room_number', flat=True))}")

                if self.room_type:
                    queryset = queryset.filter(room_type=self.room_type)
                    print(f"After room type filter count: {queryset.count()}")

                if self.room_type != 'conference':
                    if self.bed_type:
                        queryset = queryset.filter(bed_type=self.bed_type)
                else:
                    if self.seating_capacity:
                        queryset = queryset.filter(seating_capacity=self.seating_capacity)

                if self.ac_type:
                    queryset = queryset.filter(ac_type=self.ac_type)

                print(f"Final filtered queryset count: {queryset.count()}")
                return queryset

            except ValueError as e:
                print(f"Date parsing error: {e}")
                return queryset

        # Default mode: return all rooms for grouping
        print(f"Returning all rooms for grouping. Count: {queryset.count()}")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subscription_user = SubscriptionUserDetails.objects.filter(
            user=self.request.user, 
            is_active=True
        ).select_related('subscription_plan').first()

        print(f"Context - Subscription user: {subscription_user}")

        # Get the queryset
        queryset = self.get_queryset()
        print(f"Context - Queryset count: {queryset.count()}")
        print(f"Context - Room numbers: {list(queryset.values_list('room_number', flat=True))}")

        context.update({
            'user': self.request.user,
            'is_authenticated': self.request.user.is_authenticated,
            'is_admin': self.request.user.is_staff,
            'guest_id': self.request.GET.get('guest_id'),
            'check_in': self.check_in,
            'check_out': self.check_out,
            'subscription_user': subscription_user,
            'subscription_plan': subscription_user.subscription_plan if subscription_user else None,
            'room_types': RoomType.objects.filter(subscription_user=subscription_user) if subscription_user else RoomType.objects.none(),
            'bed_types': Room.BED_TYPE_CHOICES,
            'ac_types': Room.AC_CHOICES,
        })

        # Determine which context to pass
        if self.check_in and self.check_out:
            print("Setting available_rooms context")
            context['available_rooms'] = queryset
            if self.room_type:
                context['selected_room_type'] = RoomType.objects.filter(id=self.room_type).first()
        else:
            print("Setting grouped_rooms context")
            # Group rooms by room type
            grouped_rooms = defaultdict(list)
            for room in queryset:
                grouped_rooms[room.room_type].append(room)
            context['grouped_rooms'] = dict(grouped_rooms)
            print(f"Grouped rooms count: {len(context['grouped_rooms'])}")
            print(f"Grouped room types: {[rt.name for rt in context['grouped_rooms'].keys()]}")

        return context



# class RoomListView(LoginRequiredMixin, ListView):
#     model = Room
#     template_name = 'hotelapp/rooms1.html'
#     context_object_name = 'rooms'

#     def get_queryset(self):
#         # Get the active subscription user
#         subscription_user = SubscriptionUserDetails.objects.filter(
#             user=self.request.user, 
#             is_active=True
#         ).select_related('subscription_plan').first()
        
#         if not subscription_user:
#             return Room.objects.none()  # Return empty queryset if no active subscription
            
#         # Start with rooms for this subscription user
#         queryset = Room.objects.filter(
#             subscription_user=subscription_user,
#             is_available=True
#         ).select_related('subscription_plan').prefetch_related('images')
        
#         # Get filter parameters from the request
#         room_type = self.request.GET.get('room_type')
#         bed_type = self.request.GET.get('bed_type')
#         seating_capacity = self.request.GET.get('seating_capacity')
#         ac_type = self.request.GET.get('ac_type')
        
#         # Apply filters
#         if room_type:
#             queryset = queryset.filter(room_type=room_type)
        
#         if room_type != 'conference':
#             if bed_type:
#                 queryset = queryset.filter(bed_type=bed_type)
#         else:
#             if seating_capacity:
#                 queryset = queryset.filter(seating_capacity=seating_capacity)
                
#         if ac_type:
#             queryset = queryset.filter(ac_type=ac_type)
            
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get subscription details
#         subscription_user = SubscriptionUserDetails.objects.filter(
#             user=self.request.user, 
#             is_active=True
#         ).select_related('subscription_plan').first()
        
#         context.update({
#             'user': self.request.user,
#             'is_authenticated': self.request.user.is_authenticated,
#             'is_admin': self.request.user.is_staff,
#             'guest_id': self.request.GET.get('guest_id'),
#             'check_in': self.request.GET.get('check_in'),
#             'check_out': self.request.GET.get('check_out'),
#             'subscription_user': subscription_user,
#             'subscription_plan': subscription_user.subscription_plan if subscription_user else None,
#             'room_types': Room.room_type,
#             'bed_types': Room.BED_TYPE_CHOICES,
#             'ac_types': Room.AC_CHOICES,
#         })
        
#         return context

class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    template_name = 'hotelapp/room1.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch related images to optimize database queries
        context['room'] = Room.objects.prefetch_related('images').get(pk=self.object.pk)
        context['features'] = self.object.features.all()  # Fetch all related features
        print(context['features'])
        return context

# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_superuser

@login_required
def add_room(request):
    if request.method == "POST":
        addition_type = request.POST.get("additionType")

        try:
            # ✅ Get Active Subscription User
            subscription_user = SubscriptionUserDetails.objects.filter(
                user=request.user, is_active=True
            ).first()

            # ✅ Check If Subscription Exists
            if not subscription_user:
                return JsonResponse({"error": "No active subscription found."}, status=400)

            # ✅ SINGLE ROOM ADDITION
            if addition_type == "single":
                form = RoomForm(request.POST, request.FILES)
                if form.is_valid():
                    with transaction.atomic():  # Ensure atomicity
                        room_type_id = request.POST.get("room_type")
                        room_type = RoomType.objects.get(id=room_type_id)

                        room = form.save(commit=False)
                        room.subscription_user = subscription_user
                        room.room_type = room_type

                        # ✅ If RoomType is "conference", ensure seating_capacity is set
                        if room_type.bed_type == "conference":
                            room.bed_type = None

                            room.seating_capacity = request.POST.get("seating_capacity", 0)

                        room.save()  # 🔥 Save the room

                        # ✅ Handle ManyToMany Features
                        features = request.POST.getlist("features")
                        if features:
                            room.features.set(features)

                        # ✅ Save Room Images
                        images = request.FILES.getlist("images")
                        for image in images:
                            RoomImage.objects.create(room=room, image=image, subscription_user=subscription_user)

                    return JsonResponse({"success": "Room added successfully!"})

                logger.error(f"Form validation failed: {form.errors}")
                return JsonResponse({"error": form.errors}, status=400)

            # ✅ BULK ROOM ADDITION
            elif addition_type == "bulk":
                bulk_form = BulkRoomForm(request.POST)
                if bulk_form.is_valid():
                    from_room = int(bulk_form.cleaned_data['from_room_number'])
                    to_room = int(bulk_form.cleaned_data['to_room_number'])
                    block = request.POST.get('block')
                    room_type_id = request.POST.get('room_type')

                    try:
                        room_type = RoomType.objects.get(id=room_type_id)
                    except RoomType.DoesNotExist:
                        return JsonResponse({"error": "Invalid Room Type"}, status=400)

                    logger.info(f"Creating bulk rooms from {from_room} to {to_room} in block {block}.")

                    created_rooms = []

                    try:
                        with transaction.atomic():
                            for room_number in range(from_room, to_room + 1):
                                try:
                                    seating_capacity = request.POST.get("seating_capacity")
                                    seating_capacity = int(seating_capacity) if seating_capacity and seating_capacity.strip() else None

                                    new_room = Room(
                                        room_number=str(room_number),
                                        block=block,
                                        subscription_user=subscription_user,
                                        room_type=room_type,
                                        bed_type=request.POST.get("bed_type"),
                                        ac_type=request.POST.get("ac_type"),
                                        base_price=request.POST.get("base_price"),
                                        weekend_price=request.POST.get("weekend_price"),
                                        holiday_price=request.POST.get("holiday_price"),
                                        hourly_price=request.POST.get("hourly_price"),
                                        max_occupancy=request.POST.get("max_occupancy"),
                                        seating_capacity=seating_capacity if room_type.bed_type == "conference" else None,
                                        description=request.POST.get("description"),
                                        is_available=True
                                    )

                                    new_room.save()

                                    # ✅ Handle ManyToManyField Features
                                    features = Feature.objects.filter(id__in=request.POST.getlist("features"))
                                    if features:
                                        new_room.features.set(features)

                                    created_rooms.append(new_room.room_number)

                                except Exception as e:
                                    logger.error(f"Error saving Room {room_number}: {str(e)}")
                                    raise e  # 🔴 Rethrow to rollback

                        if created_rooms:
                            return JsonResponse({
                                "success": f"{len(created_rooms)} rooms added successfully!",
                                "created_rooms": created_rooms
                            })
                        else:
                            return JsonResponse({"error": "No rooms were added. Check input data."}, status=400)

                    except IntegrityError as e:
                        logger.error(f"Database transaction failed: {str(e)}")
                        return JsonResponse({"error": "Database transaction failed. Check logs."}, status=500)

                else:
                    logger.error(f"Bulk form validation failed: {bulk_form.errors}")
                    return JsonResponse({"error": bulk_form.errors}, status=400)

            return JsonResponse({"error": "Invalid addition type"}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "hotelapp/rooms1.html", {
        "form": RoomForm(),
        "bulk_form": BulkRoomForm(),
        "room_type_list": RoomType.objects.all(),
    })

# Room Add View
# @login_required
# def add_room(request):
#     # ✅ Get Active Subscription User
#     subscription_user = SubscriptionUserDetails.objects.filter(
#         user=request.user, is_active=True
#     ).first()

#     # ✅ Check If Subscription Exists
#     if not subscription_user:
#         messages.error(request, 'No active subscription found.')
#         return redirect('subscription:plans')

#     # ✅ Fetch Room Types
#     room_types = RoomType.objects.filter(subscription_user=subscription_user)

#     # ✅ Initialize Forms
#     form = RoomForm(request.POST or None, request.FILES or None)
#     bulk_form = BulkRoomForm(request.POST or None)

#     if request.method == 'POST':
#         addition_type = request.POST.get('additionType')
#         logger.info(f"Addition Type: {addition_type}")
#         logger.info(f"POST Data: {request.POST}")

#         # ✅ SINGLE ROOM ADDITION
#         if addition_type == 'single':
#             form = RoomForm(request.POST, request.FILES)
#             if form.is_valid():
#                 room_type_id = request.POST.get('room_type')
#                 room_type = RoomType.objects.get(id=room_type_id)

#                 room_number = form.cleaned_data['room_number']
#                 block = form.cleaned_data['block']

#                 # ✅ Check if Room Already Exists
#                 if Room.objects.filter(
#                     room_number=room_number, block=block, subscription_user=subscription_user
#                 ).exists():
#                     messages.error(request, f'Room number {room_number} already exists in block {block}.')
#                 else:
#                     # ✅ Save The Room
#                     room = form.save(commit=False)
#                     room.subscription_user = subscription_user
#                     room.room_type = room_type
#                     room.save()

#                     features = request.POST.getlist('features')
#                     room.features.set(features)  # Use .set() for ManyToMany fields


#                     # ✅ Save Room Images
#                     images = request.FILES.getlist('images')
#                     for image in images:
#                         RoomImage.objects.create(room=room, image=image, subscription_user=subscription_user)

#                     messages.success(request, 'Room added successfully!')
#                     return redirect('admin-panel:room_list')

#         # ✅ BULK ROOM ADDITION
#         elif addition_type == 'bulk':
#             bulk_form = BulkRoomForm(request.POST)
#             if bulk_form.is_valid():
#                 from_room = int(bulk_form.cleaned_data['from_room_number'])
#                 to_room = int(bulk_form.cleaned_data['to_room_number'])
#                 block = request.POST.get('block')
#                 room_type_id = request.POST.get('room_type')
#                 room_type = RoomType.objects.get(id=room_type_id)

#                 # ✅ Check If Rooms Already Exist
#                 existing_rooms = Room.objects.filter(
#                     room_number__in=[str(i) for i in range(from_room, to_room + 1)],
#                     block=block,
#                     subscription_user=subscription_user
#                 )

#                 if existing_rooms.exists():
#                     existing_numbers = ", ".join([room.room_number for room in existing_rooms])
#                     messages.error(request, f'Room numbers {existing_numbers} already exist in block {block}.')
#                 else:
#                     # ✅ Bulk Room Save
#                     for room_number in range(from_room, to_room + 1):
#                         new_room = Room(
#                             room_number=str(room_number),
#                             block=block,
#                             subscription_user=subscription_user,
#                             room_type=room_type,
#                             bed_type=request.POST.get('bed_type'),
#                             ac_type=request.POST.get('ac_type'),
#                             base_price=request.POST.get('base_price'),
#                             weekend_price=request.POST.get('weekend_price'),
#                             holiday_price=request.POST.get('holiday_price'),
#                             hourly_price=request.POST.get('hourly_price'),
#                             max_occupancy=request.POST.get('max_occupancy'),
#                             seating_capacity=request.POST.get('seating_capacity'),
#                             description=request.POST.get('description'),
#                             is_available=True
#                         )
#                         new_room.save()

#                         features = request.POST.getlist('features')
#                         new_room.features.set(features)  # Use .set() for ManyToMany fields

#                     messages.success(request, f'{to_room - from_room + 1} rooms added successfully!')
#                     return redirect('admin-panel:room_list')

#     # ✅ Render Form Always (Even If Error Occurs)
#     return render(request, 'hotelapp/rooms1.html', {
#         'form': form,
#         'bulk_form': bulk_form,
#         'room_type_list': room_types,
#     })


@login_required
def fetch_room_data(request):
    # Get the active subscription user for the logged-in user
    subscription_user_details = SubscriptionUserDetails.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not subscription_user_details:
        return JsonResponse({"error": "No active subscription found for the user."}, status=403)

    # Fetch room types associated with the subscription user
    room_types = RoomType.objects.filter(subscription_user=subscription_user_details).values("id", "name", "bed_type")

    # Fetch features linked to the subscription user
    features = Feature.objects.filter(subscription_user=subscription_user_details).values("id", "name")

    return JsonResponse({
        "room_types": list(room_types),
        "features": list(features)
    })

# def fetch_room_details(request):
#     room_type_id = request.GET.get("room_type_id")

#     try:
#         room = Room.objects.filter(room_type_id=room_type_id).first()
#         if room:
#             return JsonResponse({
#                 "room": {
#                     "bed_type": room.bed_type,
#                     "seating_capacity": room.seating_capacity,
#                 }
#             })
#     except Room.DoesNotExist:
#         return JsonResponse({"room": None})

#     return JsonResponse({"room": None})

@login_required
def settings_view(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)  # Get the logged-in user's subscription

        form = RoomTypeForm()  # Initialize the form
        team_designation_form = TeamDesignationForm()  # Initialize the TeamDesignationForm
        events = Event.objects.filter(subscription_user=subscription_user)  # Filter events by this user
        team_designation_list = TeamDesignation.objects.filter(subscription_user=subscription_user) # Fetch all team designation list
        room_type_list = RoomType.objects.filter(subscription_user=subscription_user)
        features_list = Feature.objects.filter(subscription_user=subscription_user)
    except SubscriptionUserDetails.DoesNotExist:
        events = []  # If user has no subscription, return an empty list
        team_designation_list=[]
        room_type_list=[]
        features_list = []


    return render(request,'hotelapp/updated-setting.html',{
        'form': form,
        'team_designation_form': team_designation_form,
        'events':events,
        'team_designation_list':team_designation_list,
        'room_type_list':room_type_list,
        'features_list':features_list,
})

# ✅ Utility Function to Avoid Context Error
def _render_with_context(request, form, bulk_form):
    subscription_user = SubscriptionUserDetails.objects.get(user=request.user)

    context = {
        'form': form,
        'bulk_form': bulk_form,
        'form_errors': form.errors if form.errors else None,
        'bulk_form_errors': bulk_form.errors if bulk_form.errors else None,
        'team_designation_form': TeamDesignationForm(),
        'events': Event.objects.filter(subscription_user=subscription_user),
        'team_designation_list': TeamDesignation.objects.filter(subscription_user=subscription_user),
        'room_type_list': RoomType.objects.filter(subscription_user=subscription_user),
        'features_list': Feature.objects.filter(subscription_user=subscription_user),
    }

    return render(request, 'hotelapp/updated-setting.html', context)
# Guest Views

@login_required
def guest_list(request):
    subscription_user_details = SubscriptionUserDetails.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not subscription_user_details:
        return render(request, 'hotelapp/guest_list.html', {
            'error': 'No active subscription found for the user.'
        })

    # Get all guests who have bookings under this subscription user
    guest_ids = Booking.objects.filter(
        subscription_user=subscription_user_details
    ).values_list('guest_id', flat=True).distinct()

    guests = Guest.objects.filter(id__in=guest_ids, subscription_user=subscription_user_details).annotate(
        total_amount=Sum('booking__total_amount')
    ).prefetch_related(
        Prefetch('booking_set', queryset=Booking.objects.filter(subscription_user=subscription_user_details))
    )

    return render(request, 'hotelapp/guest_list.html', {
        'guests': guests,
    })

# class GuestListView(LoginRequiredMixin, ListView):
#     model = Guest
#     template_name = 'hotelapp/guest_list.html'
#     context_object_name = 'guests'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['guest_id'] = self.request.GET.get('guest_id')
#         return context

def guest_register(request):
    if request.method == 'POST':
        form = GuestForm(request.POST, request.FILES)
        if form.is_valid():
            # Save form data temporarily in session
            guest_data = form.cleaned_data
            request.session['guest_registration_data'] = guest_data

            # Generate 4-digit OTP
            otp = str(random.randint(1000, 9999))
            request.session['guest_otp'] = otp

            # Send OTP to guest email
            send_mail(
                subject='Your Email Verification Code',
                message=f'Your verification code is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[guest_data['email']],
                fail_silently=False,
            )

            messages.success(request, 'Verification code sent to your email. Please enter it below.')
            return redirect('guest_verify')
    else:
        form = GuestForm()
    return render(request, 'hotelapp/guest_form.html', {'form': form})

def guest_verify(request):
    if request.method == 'POST':
        form = GuestOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            session_otp = request.session.get('guest_otp')

            if entered_otp == session_otp:
                guest_data = request.session.get('guest_registration_data')
                if guest_data:
                    guest = Guest.objects.create(
                        name=guest_data['name'],
                        phone=guest_data['phone'],
                        email=guest_data['email'],
                        address=guest_data['address'],
                        proof_type=guest_data['proof_type'],
                        proof_no=guest_data['proof_no'],
                        proof_file=request.FILES.get('proof_file'),  # re-fetch uploaded file
                    )
                    request.session['guest_id'] = guest.id

                    # Clean up session
                    del request.session['guest_registration_data']
                    del request.session['guest_otp']

                    messages.success(request, 'Registration completed successfully!')
                    return redirect('guest_dashboard')
                else:
                    messages.error(request, 'Session expired. Please register again.')
                    return redirect('guest_register')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = GuestOTPForm()
    return render(request, 'hotelapp/guest_verify.html', {'form': form})

# @login_required
# def guest_create(request):
#     subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
#     if not subscription_user:
#         messages.error(request, 'No active subscription found.')
#         return redirect('subscription:plans')

#     room_id = request.GET.get('room')
    
#     if request.method == 'POST':
#         form = GuestForm(request.POST, request.FILES)
#         if form.is_valid():
#             guest = form.save(commit=False)
#             guest.subscription_user = subscription_user
#             guest.save()
#             messages.success(request, 'Guest registered successfully!')
#             if room_id:
#                 return redirect('admin-panel:bookings', guest_id=guest.id, room_id=room_id)
#             return redirect('admin-panel:bookings', guest_id=guest.id)
#     else:
#         form = GuestForm()
    
#     return render(request, 'hotelapp/guest_form.html', {
#         'form': form,
#         'room_id': room_id
#     })

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

@method_decorator(login_required, name='dispatch')
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'hotelapp/bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Get the active subscription user details for the logged-in user
        subscription_user_details = SubscriptionUserDetails.objects.filter(
            user=self.request.user, is_active=True
        ).first()  # This will return a single instance or None

        logger.debug(f"Subscription User Details: {subscription_user_details}")

        queryset = Booking.objects.none()  # Default empty queryset
        
        if subscription_user_details:  # Check if we have a valid instance
            logger.debug(f"Filtering bookings for user ID: {subscription_user_details.id}")
            queryset = Booking.objects.filter(subscription_user=subscription_user_details)  # Corrected variable name
            queryset=queryset.select_related('guest', 'room')
            
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            logger.debug(f"Queryset: {queryset}")  # Log the queryset
            return queryset.order_by('-created_at')

        logger.debug("No active subscription user details found.")
        return queryset  # Return the empty queryset if no subscription user details found

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        
        # Add summary statistics
        context['total_bookings'] = self.get_queryset().count()
        context['total_amount'] = self.get_queryset().aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
        
        # Get the active subscription user details
        subscription_user_details = SubscriptionUserDetails.objects.filter(
            user=self.request.user, is_active=True
        ).first()
        
        # Add subscription user details to context
        context['subscription_user'] = subscription_user_details
        
        # Fetch recent bookings only if subscription user details exist
        if subscription_user_details:
            context['recent_bookings'] = Booking.objects.filter(
                subscription_user=subscription_user_details
            ).order_by('-created_at')[:5]
        else:
            context['recent_bookings'] = Booking.objects.none()
        
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

# @require_POST
# def check_room_availability(request):
#     try:
#         data = json.loads(request.body)
#         check_in = data.get('check_in')
#         check_out = data.get('check_out')
#         room_type = data.get('room_type')
#         bed_type = data.get('bed_type')
#         ac_type = data.get('ac_type')

#         # Convert check-in and check-out to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in, '%Y-%m-%dT%H:%M')
#         check_out_date = timezone.datetime.strptime(check_out, '%Y-%m-%dT%H:%M')

#         # Query to find available rooms
#         available_rooms = Room.objects.filter(is_available=True).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         # Apply filters
#         if room_type:
#             available_rooms = available_rooms.filter(room_type=room_type)
#         if bed_type:
#             available_rooms = available_rooms.filter(bed_type=bed_type)
#         if ac_type:
#             available_rooms = available_rooms.filter(ac_type=ac_type)

#         return JsonResponse({
#             'success': True,
#             'available_rooms': list(available_rooms.values('id', 'room_type', 'bed_type', 'ac_type', 'base_price'))
#         })

#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         })


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
            booking.total_amount = booking.room.base_price * max(nights, 1)

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
#@superuser_required
def add_team_member(request):
    try:
        # Get the current user's subscription details
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)

        # Debugging Information
        print(f"User: {request.user}")
        print(f"Subscription User: {subscription_user}")
        print(f"Subscription Plan: {subscription_user.subscription_plan}")

        # If no subscription plan is assigned
        if not subscription_user.subscription_plan:
            messages.warning(request, 'Please select a subscription plan to continue.')
            return redirect('subscription:plans')

        # Get current team member count
        current_members = TeamMember.objects.filter(subscription_user=subscription_user).count()
        max_members = subscription_user.subscription_plan.max_team_members
        team_designations = TeamDesignation.objects.filter(subscription_user=subscription_user)


        if request.method == 'POST':
            form = TeamMemberForm(request.POST, request.FILES, subscription_user=subscription_user)  # Pass subscription_user
            if form.is_valid():
                if current_members >= max_members:
                    messages.error(request, f'Team member limit reached ({current_members}/{max_members}). Please upgrade your plan.')
                    return redirect('admin-panel:team_list')

                # Check if a team member with the same email or phone number exists in the same subscription
                duplicate_exists = TeamMember.objects.filter(
                    subscription_user=subscription_user
                ).filter(
                    email1=form.cleaned_data['email1'],
                    subscription_user=subscription_user  # Check within the same subscription
                ).exists()

                if duplicate_exists:
                    messages.error(request, 'A team member with this email already exists in your subscription.')
                    return redirect('admin-panel:team_list')

                duplicate_phone = TeamMember.objects.filter(
                    subscription_user=subscription_user
                ).filter(
                    phone1=form.cleaned_data['phone1'],
                    subscription_user=subscription_user  # Check within the same subscription
                ).exists()

                if duplicate_phone:
                    messages.error(request, 'A team member with this phone number already exists in your subscription.')
                    return redirect('admin-panel:team_list')

                team_member = form.save(commit=False)
                team_member.subscription_user = subscription_user  # Assign to correct subscription
                try:
                    team_member.save()
                    messages.success(request, 'Team member added successfully!')
                except IntegrityError:
                    messages.error(request, 'A team member with these details already exists within your subscription.')
                    return redirect('admin-panel:team_list')

                return redirect('admin-panel:team_list')
        else:
            form = TeamMemberForm()

        context = {
            'form': form,
            'current_members': current_members,
            'max_members': max_members,
            'subscription_user': subscription_user,
            'subscription_plan': subscription_user.subscription_plan,
            'team_designations': team_designations,  # Add this line

        }
        return render(request, 'hotelapp/team-add.html', context)

    except SubscriptionUserDetails.DoesNotExist:
        messages.warning(request, 'Please subscribe to continue.')
        return redirect('subscription:plans')


def team_list(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
    if subscription_user:
        team_members = TeamMember.objects.filter(subscription_user=subscription_user)
    else:
        team_members = TeamMember.objects.none()
    
    context = {'team_members': team_members}
    return render(request, 'hotelapp/team-list.html', context)

# def team_list(request):
#     query = request.GET.get('search', '')  # Get the search query from the GET request
#     if query:
#         team_members = TeamMember.objects.filter(name__icontains=query).order_by('name')  # Filter by name
#     else:
#         team_members = TeamMember.objects.all().order_by('name')  # Get all members if no query

#     return render(request, 'hotelapp/team-list.html', {
#         'team_members': team_members
#     })

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

@login_required
def delete_team_member(request, id):
    try:
        team_member = get_object_or_404(TeamMember, id=id)
        team_member.delete()
        return JsonResponse({
            'success': True,
            'message': 'Team member deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to delete the team member.'
        })

        
# def invoice_view(request, guest_id, booking_date):
#     try:
#         parsed_date = parse_date(booking_date)
#         print("Parsed Date:", parsed_date, type(parsed_date))

#     except:
#         return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")

#     # 🔍 Fetch all bookings for the guest on the same date
#     bookings = Booking.objects.annotate(
#         local_check_in_date=TruncDate('check_in')
#     ).filter(
#         guest_id=guest_id,
#         local_check_in_date=parsed_date
#     )
    
#     print("Guest ID:", guest_id)
#     print("Parsed Date:", parsed_date)
#     print("Bookings:", bookings)

#     if not bookings.exists():
#         return HttpResponse("No bookings found.", status=404)

#     guest = bookings.first().guest
#     company = bookings.first().subscription_user

#     rooms = []
#     total = Decimal('0.00')

#     room_data = []
#     for booking in bookings:
#         rooms.append(booking.room)
#         total += booking.total_amount

#         room_image = booking.room.images.first().image.url if booking.room.images.exists() else '/static/assets/img/room/1.png'
#         room_data.append({
#             'room': booking.room,
#             'room_type': booking.room.room_type,
#             'room_image': room_image,
#         })

#     # 💰 Taxes
#     hotel_taxes = HotelTax.objects.filter(subscription_user=company)
#     platform_taxes = SubscriptionTax.objects.filter(is_platform_fee=True)
#     all_taxes = list(hotel_taxes) + list(platform_taxes)

#     total_tax_percent = sum([tax.percentage for tax in all_taxes])
#     subtotal = (total * Decimal('100')) / Decimal(100 + total_tax_percent)
#     subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#     tax_breakdown = []
#     total_tax_amount = Decimal('0.00')
#     for tax in all_taxes:
#         tax_amount = (subtotal * tax.percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         total_tax_amount += tax_amount
#         tax_breakdown.append({
#             'name': tax.name,
#             'percentage': tax.percentage,
#             'amount': tax_amount,
#             'is_platform_fee': getattr(tax, 'is_platform_fee', False),
#         })

#     # 🔧 Logos
#     logo_obj = LogoSettings.objects.filter(subscription_user=company).first()
#     dark_logo_url = logo_obj.dark_logo.url if logo_obj and logo_obj.dark_logo else '/static/assets/img/logo/full-logo.png'
#     light_logo_url = logo_obj.light_logo.url if logo_obj and logo_obj.light_logo else '/static/assets/img/logo/collapse-logo.png'

#     context = {
#         'guest': guest,
#         'rooms': rooms,
#         'room_data': room_data,
#         'company': company,
#         'subtotal': subtotal,
#         'tax_breakdown': tax_breakdown,
#         'total_tax_amount': total_tax_amount,
#         'total': total,
#         'dark_logo_url': dark_logo_url,
#         'light_logo_url': light_logo_url,
#         'theme': 'light',
#         'check_in': parsed_date,
#     }

#     return render(request, 'hotelapp/invoice.html', context)

def invoice_detail_view(request, invoice_id):
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room', 'subscription_user', 'room__room_type'),
        invoice_id=invoice_id
    )

    guest = booking.guest
    subscription_user = booking.subscription_user

    room = booking.room
    total = booking.total_amount

    room_image = room.images.first().image.url if room.images.exists() else '/static/assets/img/room/1.png'

    room_data = [{
        'room': room,
        'room_type': room.room_type,
        'room_image': room_image,
    }]

    # Taxes
    hotel_taxes = HotelTax.objects.filter(subscription_user=subscription_user)
    platform_taxes = SubscriptionTax.objects.filter(is_platform_fee=True)
    all_taxes = list(hotel_taxes) + list(platform_taxes)

    total_tax_percent = sum([tax.percentage for tax in all_taxes])
    subtotal = (total * Decimal('100')) / Decimal(100 + total_tax_percent)
    subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    tax_breakdown = []
    total_tax_amount = Decimal('0.00')
    for tax in all_taxes:
        tax_amount = (subtotal * tax.percentage / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_tax_amount += tax_amount
        tax_breakdown.append({
            'name': tax.name,
            'percentage': tax.percentage,
            'amount': tax_amount,
        })

    # Logos
    theme = request.GET.get('theme', 'light')
    logo_obj = LogoSettings.objects.filter(subscription_user=subscription_user).first()
    dark_logo_url = logo_obj.dark_logo.url if logo_obj and logo_obj.dark_logo else '/static/assets/img/logo/full-logo.png'
    light_logo_url = logo_obj.light_logo.url if logo_obj and logo_obj.light_logo else '/static/assets/img/logo/collapse-logo.png'

    context = {
        'guest': guest,
        'booking': booking,
        'room_data': room_data,
        'company': subscription_user,
        'subtotal': subtotal,
        'tax_breakdown': tax_breakdown,
        'total_tax_amount': total_tax_amount,
        'total': total,
        'dark_logo_url': dark_logo_url,
        'light_logo_url': light_logo_url,
        'theme': theme,
    }

    return render(request, 'hotelapp/invoice.html', context)

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

def invoice_list_view(request):
    # Get the current user's subscription details
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
    
    if not subscription_user:
        messages.error(request, 'You do not have an active subscription.')
        return redirect('subscription:plans')

    # Fetch all bookings for the current user
    bookings = Booking.objects.filter(subscription_user=subscription_user).select_related('guest', 'room')

    return render(request, 'hotelapp/invoice_list.html', {
        'bookings': bookings,
        'subscription_user': subscription_user,
    })

def menu_view(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
    if subscription_user:
        breakfast_items = FoodItem.objects.filter(subscription_user=subscription_user, category='breakfast')
        lunch_items = FoodItem.objects.filter(subscription_user=subscription_user, category='lunch')
        dinner_items = FoodItem.objects.filter(subscription_user=subscription_user, category='dinner')
    else:
        breakfast_items = FoodItem.objects.none()
        lunch_items = FoodItem.objects.none()
        dinner_items = FoodItem.objects.none()
    
    return render(request, 'hotelapp/menu.html', {
        'breakfast_items': breakfast_items,
        'lunch_items': lunch_items,
        'dinner_items': dinner_items,
    })

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
    # Get email and secret_key from URL parameters
    email = request.GET.get('email')
    secret_key = request.GET.get('secret_key')
    
    print("Full GET parameters:", request.GET)
    print(f"Captured Email: {email}, Secret Key: {secret_key}")
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email', email)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        privacy_policy = request.POST.get('privacy_policy')
        secret_key = request.POST.get('secret_key', secret_key)

        try:
            # Verify subscription details first
            subscription = SubscriptionUserDetails.objects.get(
                email=email,
                secret_key=secret_key,
                is_active=True
            )
            
            # Get the associated cart and plan
            cart = Cart.objects.filter(user_details=subscription).first()
            if not cart:
                messages.error(request, 'No subscription plan found.')
                return redirect('subscription:plans')
                
            subscription_type = cart.plan.name.lower()  # Get plan name from cart
            
            if subscription.is_key_used:
                messages.warning(request, 'This registration link has already been used. Please login instead.')
                return redirect('admin-panel:login')

            # Validate form data
            if not all([first_name, last_name, username, email, password, password2]):
                messages.error(request, 'All fields are required.')
                return render(request, 'hotelapp/signup.html', {
                    'email': email,
                    'secret_key': secret_key,
                    'form_data': request.POST
                })

            if not privacy_policy:
                messages.error(request, 'You must agree to the privacy policy.')
                return render(request, 'hotelapp/signup.html', {
                    'email': email,
                    'secret_key': secret_key,
                    'form_data': request.POST
                })

            if password != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'hotelapp/signup.html', {
                    'email': email,
                    'secret_key': secret_key,
                    'form_data': request.POST
                })

            # Create new user with subscription type as user_type
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
               # user_type=subscription_type  # Use plan name as user type
            )

            # Update subscription with user reference
            subscription.user = user
            subscription.mark_key_as_used()
            subscription.save()

            messages.success(request, 'Registration successful! Please login.')
            return redirect('admin-panel:login')

        except SubscriptionUserDetails.DoesNotExist:
            messages.error(request, 'Invalid subscription details.')
            return redirect('subscription:plans')
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            messages.error(request, f'An error occurred during registration. Please try again.')
            return render(request, 'hotelapp/signup.html', {
                'email': email,
                'secret_key': secret_key,
                'form_data': request.POST
            })

    # For GET request
    try:
        # Get subscription details for the template
        subscription = SubscriptionUserDetails.objects.get(
            email=email,
            secret_key=secret_key,
            is_active=True
        )
        
        # Get the associated cart and plan
        cart = Cart.objects.filter(user_details=subscription).first()
        if not cart:
            messages.error(request, 'No subscription plan found.')
            return redirect('subscription:plans')
            
        subscription_type = cart.plan.name  # Get plan name from cart
        
        context = {
            'email': email,
            'secret_key': secret_key,
            'subscription_type': subscription_type
        }
    except SubscriptionUserDetails.DoesNotExist:
        messages.error(request, 'Invalid subscription details.')
        return redirect('subscription:plans')
        
    return render(request, 'hotelapp/signup.html', context)


def login_view(request, guest=None):
    print("Login view called")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Login attempt for user: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"User authenticated: {user.username}")

            # Redirect based on user type
            if user.is_superuser:
                print("Redirecting to superuser dashboard")
                return redirect('subscription:super_admin')  # Replace with your actual superuser URL

            elif getattr(user, 'is_guest', False):
                print("Redirecting to guest dashboard")
                guest = getattr(user, 'guest_profile', None)
                if guest:
                        return redirect('subscription:guest_view', guest.id)
                else:
                    messages.error(request, 'Guest profile not found.')
                    return redirect('hotelapp:login')  # or wherever appropriate    
            else:
                # Regular admin with subscriptions
                subscriptions = SubscriptionUserDetails.objects.filter(
                    user=user,
                    is_active=True
                ).select_related('subscription_plan')

                print(f"Found {subscriptions.count()} active subscriptions")

                if subscriptions.exists():
                    if subscriptions.count() > 1:
                        subscription_list = [
                            {
                                'id': sub.id,
                                'company_name': sub.company_name,
                                'plan_name': sub.subscription_plan.name if sub.subscription_plan else 'No Plan'
                            }
                            for sub in subscriptions
                        ]
                        request.session['available_subscriptions'] = subscription_list
                        print("Multiple subscriptions found, redirecting to selection")
                        return redirect('admin-panel:select_subscription')
                    else:
                        subscription = subscriptions.first()
                        request.session['active_subscription_id'] = subscription.id
                        print(f"Single subscription set: {subscription.id}")
                        return redirect('admin-panel:index')
                else:
                    print("No active subscriptions found")
                    messages.info(request, 'Please select a subscription plan to continue.')
                    return redirect('subscription:plans')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'hotelapp/login.html')


@login_required
def select_subscription(request):
    """View for selecting which subscription to use"""
    print("Select subscription view called")
    
    available_subscriptions = request.session.get('available_subscriptions', [])
    print(f"Available subscriptions: {available_subscriptions}")
    
    if not available_subscriptions:
        messages.error(request, 'No subscriptions found.')
        return redirect('subscription:plans')
    
    if request.method == 'POST':
        selected_id = request.POST.get('subscription_id')
        print(f"Selected subscription ID: {selected_id}")
        
        if selected_id:
            # Verify the subscription exists and belongs to the user
            subscription = SubscriptionUserDetails.objects.filter(
                id=selected_id,
                user=request.user,
                is_active=True
            ).first()
            
            if subscription:
                request.session['active_subscription_id'] = subscription.id
                print(f"Active subscription set to: {subscription.id}")
                return redirect('admin-panel:index')
    
    return render(request, 'subscription/plans.html', {
        'subscriptions': available_subscriptions
    })

# Add this to your middleware or context processor
def get_active_subscription(request):
    """Get the currently active subscription for the user"""
    if not request.user.is_authenticated:
        return None
        
    subscription_id = request.session.get('active_subscription_id')
    if subscription_id:
        return SubscriptionUserDetails.objects.filter(
            id=subscription_id,
            user=request.user,
            is_active=True
        ).select_related('subscription_plan').first()
    return None

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


# @login_required
# def index_view(request):
#     context = {
#         'user': request.user,
#         'is_authenticated': request.user.is_authenticated,
#         # Add any other context data you need
#     }
#     return render(request, 'hotelapp/index.html', context)


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
            post_data = request.POST.copy()
            selected_rooms = json.loads(post_data.get('selectedRooms', '[]'))

            if not selected_rooms:
                return JsonResponse({'success': False, 'error': 'Room selection is required.'})

            subscription_user_details = SubscriptionUserDetails.objects.filter(
                user=request.user, is_active=True
            ).first()
            if not subscription_user_details:
                return JsonResponse({'success': False, 'error': 'No active subscription found for the user.'})

            guest_form = GuestForm(post_data, request.FILES)
            booking_form = BookingForm(post_data)

            if not guest_form.is_valid():
                return JsonResponse({'success': False, 'error': 'Invalid guest information', 'errors': guest_form.errors})
            if not booking_form.is_valid():
                return JsonResponse({'success': False, 'error': 'Invalid booking information', 'errors': booking_form.errors})

            check_in = booking_form.cleaned_data['check_in']
            check_out = booking_form.cleaned_data['check_out']

            check_in = timezone.make_aware(check_in) if timezone.is_naive(check_in) else check_in
            check_out = timezone.make_aware(check_out) if timezone.is_naive(check_out) else check_out

            if check_in < timezone.now():
                return JsonResponse({'success': False, 'error': 'Check-in time cannot be in the past.'})
            if check_out <= check_in:
                return JsonResponse({'success': False, 'error': 'Check-out time must be after check-in time.'})

            with transaction.atomic():
                guest = guest_form.save(commit=False)
                guest.subscription_user = subscription_user_details
                guest.save()

                base_total_amount = Decimal('0.00')
                bookings = []

                for room_data in selected_rooms:
                    room_type_id = room_data['roomType']
                    bed_type = room_data.get('bedType')
                    ac_type = room_data.get('acType')
                    room_count = int(room_data.get('roomCount', 1))
                    seating_capacity = room_data.get('seating_capacity')

                    room_type = RoomType.objects.get(id=room_type_id, subscription_user=subscription_user_details)

                    query = Q(room_type=room_type, ac_type=ac_type, subscription_user=subscription_user_details)

                    if room_type.bed_type.lower() == "conference":
                        bed_type = None
                        if seating_capacity:
                            query &= Q(seating_capacity=seating_capacity)
                    elif bed_type:
                        query &= Q(bed_type=bed_type)

                    overlapping_rooms = Booking.objects.filter(
                        check_in__lt=check_out,
                        check_out__gt=check_in
                    ).values_list('room_id', flat=True)

                    available_rooms = Room.objects.filter(query).exclude(id__in=overlapping_rooms).distinct()
                    available_count = available_rooms.count()

                    if available_count < room_count:
                        raise ValidationError(
                            f'Only {available_count} {room_type} rooms are available with '
                            f'{"bed type " + bed_type if bed_type else "no specific bed type"} '
                            f'and AC type {ac_type} for the selected dates. '
                            f'You requested {room_count} room(s).'
                        )

                    selected_available_rooms = available_rooms[:room_count]

                    total_hours = (check_out - check_in).total_seconds() / 3600
                    is_same_day = check_in.date() == check_out.date()
                    is_hourly = is_same_day and total_hours <= 10
                    is_holiday = Event.objects.filter(
                        start_date__lte=check_in.date(), end_date__gte=check_in.date()
                    ).exists()
                    is_weekend = check_in.weekday() in [5, 6]

                    for room in selected_available_rooms:
                        nights = max((check_out - check_in).days, 1)

                        if is_hourly:
                            price = float(total_hours) * float(room.hourly_price)
                        elif is_holiday:
                            price = float(room.holiday_price)
                        elif is_weekend:
                            price = float(room.weekend_price)
                        else:
                            price = float(room.base_price) * nights

                        price_decimal = Decimal(str(price))
                        booking = Booking(
                            guest=guest,
                            room=room,
                            check_in=check_in,
                            check_out=check_out,
                            adults=booking_form.cleaned_data['adults'],
                            children=booking_form.cleaned_data['children'],
                            payment_type=booking_form.cleaned_data['payment_type'],
                            total_amount=price_decimal,
                            subscription_user=subscription_user_details
                        )

                        if room.room_type.bed_type == "conference":
                            booking.seating_capacity = room.seating_capacity

                        bookings.append(booking)
                        base_total_amount += price_decimal

                # 🔢 1. Fetch platform and hotel taxes
                platform_taxes = SubscriptionTax.objects.filter(is_platform_fee=True)
                hotel_taxes = HotelTax.objects.filter(subscription_user=subscription_user_details)
                all_taxes = list(platform_taxes) + list(hotel_taxes)

                # 💰 2. Calculate total tax
                total_tax_amount = Decimal('0.00')
                for tax in all_taxes:
                    tax_amount = (base_total_amount * tax.percentage) / Decimal('100')
                    total_tax_amount += tax_amount

                grand_total = base_total_amount + total_tax_amount

                # 🧾 3. Proportionally distribute tax to each booking  
                for booking in bookings:
                    proportion = booking.total_amount / base_total_amount if base_total_amount > 0 else Decimal('0.00')
                    tax_share = total_tax_amount * proportion
                    booking.total_amount += tax_share

                    booking.invoice_id = generate_invoice_id()


                Booking.objects.bulk_create(bookings)
                guest.total_amount = grand_total
                guest.save()

            for booking in bookings:
                send_invoice_email(booking, request)

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('admin-panel:booking_list'),
                'message': f'Successfully booked {len(bookings)} room(s).'
            })

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    else:
        guest_form = GuestForm()
        booking_form = BookingForm()
        return render(request, 'hotelapp/bookings.html', {
            'guest_form': guest_form,
            'booking_form': booking_form,
        })


def get_room_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("🔍 Received Request Data:", data)

            room_type_name = data.get('roomType')  # ✅ Match the frontend key names
            ac_type = data.get('acType')
            bed_type = data.get('bedType')
            check_in = data.get('checkIn')
            check_out = data.get('checkOut')

            if not all([room_type_name, ac_type, bed_type, check_in, check_out]):
                return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)

            # ✅ Fetch Room Type ID correctly
            try:
                room_type_obj = RoomType.objects.get(id=room_type_name)  # Assuming ID is sent
            except RoomType.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid room type'}, status=400)

            # ✅ Fetch Available Rooms
            available_rooms = Room.objects.filter(
                room_type=room_type_obj, ac_type=ac_type, bed_type=bed_type, is_available=True
            ).exclude(
                bookings__check_in__lt=check_out, bookings__check_out__gt=check_in
            ).count()

            return JsonResponse({'success': True, 'availability': available_rooms})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Server Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def get_room_types(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
        if not subscription_user:
            return JsonResponse({"success": False, "error": "Subscription user not found"}, status=404)

        # Filter RoomTypes based on rooms owned by the subscription_user
        room_types = RoomType.objects.filter(
            rooms__subscription_user=subscription_user
        ).distinct().values("id", "name", "bed_type")

        return JsonResponse({"success": True, "room_types": list(room_types)})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ✅ Fetch a specific room type's bed_type
def get_room_bed_type(request, room_type_id):
    try:
        print(f"Fetching RoomType for ID: {room_type_id}")  # Debugging log
        room_type = get_object_or_404(RoomType, id=room_type_id)
        return JsonResponse({"success": True, "bed_type": room_type.bed_type})
    except Exception as e:
        print(f"Error fetching RoomType: {str(e)}")  # Debugging log
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def get_seating_capacities(request):
    room_type_id = request.GET.get('roomTypeId')

    try:
        # Fetch unique seating capacities from the Room model
        seating_capacities = Room.objects.filter(room_type_id=room_type_id).values_list('seating_capacity', flat=True).distinct()

        return JsonResponse({'seating_capacities': list(seating_capacities)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_room_price(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received Data:", data)

            room_type_id = data.get("roomTypeId")
            bed_type = data.get("bedType")
            ac_type = data.get("acType")
            check_in = data.get("checkIn")
            check_out = data.get("checkOut")
            seating_capacity = data.get("seatingCapacity")  # Optional

            if not all([room_type_id, ac_type, check_in, check_out]):
                return JsonResponse({"success": False, "error": "Missing required parameters"}, status=400)

            check_in_date = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%dT%H:%M")

            if check_in_date >= check_out_date:
                return JsonResponse({"success": False, "error": "Invalid check-in/check-out range"}, status=400)

            is_same_day = check_in_date.date() == check_out_date.date()
            total_hours = (check_out_date - check_in_date).total_seconds() / 3600

            subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
            if not subscription_user:
                return JsonResponse({"success": False, "error": "Subscription user not found"}, status=404)

            try:
                room_type = RoomType.objects.get(id=room_type_id, subscription_user=subscription_user)
            except RoomType.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invalid room type for this subscription"}, status=400)

            if room_type.bed_type.lower() == "conference":
                bed_type = None

            rooms = Room.objects.filter(room_type=room_type, subscription_user=subscription_user)
            if bed_type:
                rooms = rooms.filter(bed_type=bed_type)
            if ac_type:
                rooms = rooms.filter(ac_type=ac_type)

            overlapping_room_ids = Booking.objects.filter(
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            ).values_list('room_id', flat=True)

            available_rooms = rooms.exclude(id__in=overlapping_room_ids)
            room_for_price = None

            if available_rooms.exists():
                room_for_price = available_rooms.first()
                availability_text = available_rooms.count()
            else:
                fallback_rooms = rooms
                if fallback_rooms.exists():
                    room_for_price = fallback_rooms.first()
                    availability_text = "No available rooms"
                else:
                    base_price = getattr(room_type, "base_price", 0)
                    weekend_price = getattr(room_type, "weekend_price", base_price)
                    holiday_price = getattr(room_type, "holiday_price", weekend_price)
                    hourly_price = getattr(room_type, "hourly_price", base_price / 10)

                    is_holiday = Event.objects.filter(
                        start_date__lte=check_in_date.date(),
                        end_date__gte=check_in_date.date()
                    ).exists()

                    if is_holiday:
                        price = holiday_price
                    elif check_in_date.weekday() in [5, 6]:
                        price = weekend_price
                    else:
                        price = base_price

                    if is_same_day and total_hours <= 10:
                        price = float(total_hours) * float(hourly_price)

                    # 🔥 Compute tax breakdown
                    tax_breakdown, total_tax = calculate_taxes(price, subscription_user)

                    return JsonResponse({
                        "success": True,
                        "price": float(price),
                        "tax_breakdown": tax_breakdown,
                        "total_with_tax": round(price + total_tax, 2),
                        "available_rooms": "No available rooms"
                    })

            is_holiday = Event.objects.filter(
                start_date__lte=check_in_date.date(),
                end_date__gte=check_in_date.date()
            ).exists()

            if is_holiday:
                price = room_for_price.holiday_price
            elif check_in_date.weekday() in [5, 6]:
                price = room_for_price.weekend_price
            else:
                price = room_for_price.base_price

            if is_same_day and total_hours <= 10:
                price = float(total_hours) * float(room_for_price.hourly_price)

            tax_breakdown, total_tax = calculate_taxes(price, subscription_user)

            return JsonResponse({
                "success": True,
                "price": float(price),
                "tax_breakdown": tax_breakdown,
                "total_with_tax": round(price + total_tax, 2),
                "available_rooms": availability_text
            })

        except Exception as e:
            print(f"⚠️ Error in get_room_price: {str(e)}")
            return JsonResponse({"success": False, "error": f"Server error: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

def calculate_taxes(base_price, subscription_user):
    tax_breakdown = []
    total_tax = 0

    # 1. Subscription-user-specific taxes (e.g., CGST, SGST)
    user_taxes = HotelTax.objects.filter(subscription_user=subscription_user)
    for tax in user_taxes:
        tax_amount = (base_price * tax.percentage) / 100
        total_tax += tax_amount
        tax_breakdown.append({
            "name": tax.name,
            "percentage": tax.percentage,
            "amount": round(tax_amount, 2)
        })

    # 2. Platform taxes (is_platform_fee=True)
    platform_taxes = SubscriptionTax.objects.filter(is_platform_fee=True)
    for tax in platform_taxes:
        tax_amount = (base_price * tax.percentage) / 100
        total_tax += tax_amount
        tax_breakdown.append({
            "name": tax.name,
            "percentage": tax.percentage,
            "amount": round(tax_amount, 2)
        })

    return tax_breakdown, total_tax


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
                return redirect('admin-panel:settings_view')
                
        except Exception as e:
            messages.error(request, f'Error deleting booking: {str(e)}')
            return redirect('admin-panel:booking_list')
    
    return render(request, 'hotelapp/delete_booking.html', {
        'booking': booking
    })

@login_required
@superuser_required
def add_food_item(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
    if not subscription_user:
        messages.error(request, 'No active subscription found')
        return redirect('subscription:plans')

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.subscription_user = subscription_user
            food_item.save()
            messages.success(request, 'Food item added successfully!')
            return redirect('admin-panel:menu')
        else:
            messages.error(request, 'There was an error adding the food item.')
    else:
        form = FoodItemForm()
    
    return render(request, 'hotelapp/menu.html', {'form': form})

def menu_view(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
    if subscription_user:
        breakfast_items = FoodItem.objects.filter(subscription_user=subscription_user, category='breakfast')
        lunch_items = FoodItem.objects.filter(subscription_user=subscription_user, category='lunch')
        dinner_items = FoodItem.objects.filter(subscription_user=subscription_user, category='dinner')
    else:
        breakfast_items = FoodItem.objects.none()
        lunch_items = FoodItem.objects.none()
        dinner_items = FoodItem.objects.none()
    
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

import traceback
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, RoomImage  # Update with your actual import paths

logger = logging.getLogger(__name__)

@login_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        try:
            print("🔧 [Step 1] Starting room update")

            # ✅ Update basic room details
            print("🔧 [Step 2] Assigning text/ID fields")
            room.room_number = request.POST.get('room_number')
            room.block = request.POST.get('block')
            room.room_type_id = request.POST.get('room_type')
            room.bed_type = request.POST.get('bed_type')
            room.ac_type = request.POST.get('ac_type')

            print("🔧 [Step 3] Assigning price fields")
            room.base_price = Decimal(request.POST.get('base_price', '0'))
            room.weekend_price = Decimal(request.POST.get('weekend_price', '0'))
            room.holiday_price = Decimal(request.POST.get('holiday_price', '0'))
            room.hourly_price = Decimal(request.POST.get('hourly_price', '0'))

            print("🔧 [Step 4] Occupancy & description")
            room.max_occupancy = request.POST.get('max_occupancy')
            room.description = request.POST.get('description')

            # ✅ Handle ManyToMany Features
            print("🔧 [Step 5] Updating features")
            features = request.POST.getlist('features', [])
            print(f"📌 Features received: {features}")
            room.features.set(features)

            # ✅ Handle images
            print("🔧 [Step 6] Checking for new images")
            images = request.FILES.getlist('images')
            if images:
                print("🖼️ Deleting old images")
                room.images.all().delete()
                print(f"🖼️ Uploading {len(images)} new images")
                for image in images:
                    RoomImage.objects.create(
                        room=room, 
                        image=image,
                        subscription_user=room.subscription_user
                    )

            print("🔧 [Step 7] Saving room object")
            room.save()
            print("✅ Room saved successfully")

            # ✅ Return JSON if AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': True, 'redirect': reverse('admin-panel:room_list')})

        except Exception as e:
            error_message = f"❌ Room Update Error: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(error_message)
            logger.error(stack_trace)
            print(error_message)
            print(stack_trace)
            return JsonResponse({'success': False, 'error': str(e)})

    # ✅ GET Request: Return room data
    data = {
        'id': room.id,
        'room_number': room.room_number,
        'block': room.block,
        'room_type': room.room_type.id if room.room_type else None,
        'room_type_bed_type': room.room_type.bed_type if room.room_type else None,  # ✅ add this
        'room_type_name': room.room_type.name if room.room_type else None,   
        'bed_type': room.bed_type,
        'seating_capacity': room.seating_capacity,  # ✅ add this

        'ac_type': room.ac_type,
        'base_price': str(room.base_price),
        'weekend_price': str(room.weekend_price),
        'holiday_price': str(room.holiday_price),
        'hourly_price': str(room.hourly_price),
        'max_occupancy': room.max_occupancy,
        'description': room.description,
        'features': list(room.features.values_list("id", flat=True)),
        'images': [{'id': img.id, 'url': img.image.url} for img in room.images.all()],
    }

    print("🚀 Debug Room Type ID:", data["room_type"])
    print("🚀 Debug Feature IDs:", data["features"])

    return JsonResponse(data)



@login_required
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
def delete_guest(request, id):
    try:
        guest = get_object_or_404(Guest, id=id)
        guest.delete()
        return JsonResponse({'success': True, 'message': 'Guest deleted successfully!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def guest_detail(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    bookings = guest.booking_set.all()
    
    context = {
        'guest': guest,
        'bookings': bookings,
    }
    return render(request, 'hotelapp/guest-details.html', context)


@login_required
def check_availability(request):
    subscription_user = SubscriptionUserDetails.objects.filter(
        user=request.user, is_active=True
    ).select_related('subscription_plan').first()

    if not subscription_user:
        messages.error(request, 'No active subscription found.')
        return redirect('subscription:plans')

    room_types = RoomType.objects.filter(subscription_user=subscription_user)
    available_rooms = None
    grouped_rooms = {}  
    check_in_date = None
    check_out_date = None
    selected_room_type = None

    if request.method == 'GET':
        check_in_date_str = request.GET.get('check_in')
        check_out_date_str = request.GET.get('check_out')
        room_type_id = request.GET.get('room_type')

        try:
            check_in_date = timezone.make_aware(
                timezone.datetime.strptime(check_in_date_str, '%Y-%m-%dT%H:%M')
            )
            check_out_date = timezone.make_aware(
                timezone.datetime.strptime(check_out_date_str, '%Y-%m-%dT%H:%M')
            )
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format. Please try again.")
            return redirect('hotelapp:room_list')

        # Fetch rooms that are NOT booked within the given time frame
        available_rooms = Room.objects.filter(
            subscription_user=subscription_user,
            is_available=True  # Only show available rooms in availability check
        ).exclude(
            bookings__check_in__lt=check_out_date,
            bookings__check_out__gt=check_in_date
        ).distinct()

        # Apply room type filter if selected
        if room_type_id:
            available_rooms = available_rooms.filter(room_type_id=room_type_id)
            selected_room_type = RoomType.objects.filter(id=room_type_id).first()

    else:
        # Group available rooms by `room_type`
        all_rooms = Room.objects.filter(
            subscription_user=subscription_user,
            is_available=True  # Only show available rooms in grouped view
        ).select_related('room_type').prefetch_related('images')

        grouped_rooms = defaultdict(list)
        for room in all_rooms:
            grouped_rooms[room.room_type].append(room)

    return render(request, 'hotelapp/rooms1.html', {
        'available_rooms': available_rooms,  
        'grouped_rooms': dict(grouped_rooms),  
        'room_type_list': room_types,
        'selected_room_type': selected_room_type,
        'check_in': check_in_date,
        'check_out': check_out_date,
    })

# @login_required
# def check_availability(request):

#     subscription_user = SubscriptionUserDetails.objects.filter(user=request.user, is_active=True).first()
#     if not subscription_user:
#         messages.error(request, 'No active subscription found.')
#         return redirect('subscription:plans')

#     room_types = RoomType.objects.filter(subscription_user=subscription_user)

#     available_rooms = None  # Initialize available_rooms

#     if request.method == 'POST':
#         check_in_date = request.POST.get('check_in')
#         check_out_date = request.POST.get('check_out')
#         room_type = request.POST.get('room_type')

#         # Convert to datetime objects
#         check_in_date = timezone.datetime.strptime(check_in_date, '%Y-%m-%dT%H:%M')
#         check_out_date = timezone.datetime.strptime(check_out_date, '%Y-%m-%dT%H:%M')

#         # Retrieve the active subscription user details for the logged-in user
#         subscription_user_details = SubscriptionUserDetails.objects.filter(
#             user=request.user, is_active=True
#         ).first()

#         if not subscription_user_details:
#             return render(request, 'hotelapp/rooms1.html', {
#                 'error': 'No active subscription found for the user.'
#             })

#         # Query to find available rooms based on filters and subscription user
#         available_rooms = Room.objects.filter(
#             subscription_user=subscription_user_details,
#             is_available=True
#         ).exclude(
#             booking__check_in__lt=check_out_date,
#             booking__check_out__gt=check_in_date
#         )

#         # Apply room type filter if selected
#         if room_type:
#             available_rooms = available_rooms.filter(room_type=room_type)

#     return render(request, 'hotelapp/rooms1.html', {
#         'available_rooms': available_rooms,
#         'room_type_list': room_types,
#         'check_in': check_in_date if request.method == 'POST' else None,
#         'check_out': check_out_date if request.method == 'POST' else None,
#         # 'room_type': room_type,
#     })

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

# @method_decorator(login_required, name='dispatch')
# class DashboardView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         try:
#             # Get the active subscription details for the current user
#             subscription_details = SubscriptionUserDetails.objects.get(user=user, is_active=True)

#             # Get the subscription plan directly from SubscriptionUserDetails
#             subscription_plan = subscription_details.subscription_plan

#             # Get subscription limits
#             max_rooms = subscription_plan.max_rooms if subscription_plan else 0
#             max_team_members = subscription_plan.max_team_members if subscription_plan else 0

#             # Get counts - Filter by subscription_user
#             total_rooms = Room.objects.filter(subscription_user=subscription_details).count()
#             active_bookings = Booking.objects.filter(
#                 subscription_user=subscription_details,
#                 status='confirmed'
#             ).count()
#             team_members = TeamMember.objects.filter(
#                 subscription_user=subscription_details
#             ).count()

#             # Get recent bookings for the table
#             recent_bookings = Booking.objects.filter(
#                 subscription_user=subscription_details
#             ).select_related(
#                 'guest', 'room'
#             ).order_by('-created_at')[:10]  # Get last 10 bookings

#             # Calculate revenue statistics
#             total_revenue = Booking.objects.filter(
#                 subscription_user=subscription_details,
#                 status='confirmed'
#             ).aggregate(
#                 total=models.Sum('total_amount')
#             )['total'] or 0

#             # Get subscription features
#             subscription_features = subscription_plan.get_feature_list() if subscription_plan else []

#             context = {
#                 'subscription': subscription_plan,
#                 'subscription_end_date': subscription_details.subscription_end_date,
#                 'total_rooms': total_rooms,
#                 'max_rooms': max_rooms,
#                 'active_bookings': active_bookings,
#                 'team_members': team_members,
#                 'max_team_members': max_team_members,
#                 'subscription_features': subscription_features,
#                 'has_subscription': True,
#                 'recent_bookings': recent_bookings,
#                 'total_revenue': total_revenue,
#                 'company_name': subscription_details.company_name if subscription_details.company_name else "Your Hotel"
#             }

#         except SubscriptionUserDetails.DoesNotExist:
#             # Handle case where user has no subscription
#             context = {
#                 'subscription': None,
#                 'subscription_end_date': None,
#                 'total_rooms': 0,
#                 'max_rooms': 0,
#                 'active_bookings': 0,
#                 'team_members': 0,
#                 'max_team_members': 0,
#                 'subscription_features': [],
#                 'has_subscription': False,
#                 'recent_bookings': [],
#                 'total_revenue': 0,
#                 'company_name': "Your Hotel"
#             }

#         return render(request, 'hotelapp/index.html', context)

@login_required
def base_view(request):
    # Print the current user for debugging
    print("Current User ID:", request.user.id)

    # Attempt to retrieve the subscription user details
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()
    
    # Debugging: Print the retrieved subscription user
    if subscription_user:
        print("Found Subscription User:", subscription_user)
        logo_settings = LogoSettings.objects.filter(subscription_user=subscription_user).first()
    else:
        print("No Subscription User found for this account.")
        logo_settings = None

    # Debugging: Print logo settings
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

# @method_decorator(login_required, name='dispatch')
# class DashboardView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         try:
#             # Get the active subscription details for the current user
#             subscription_details = SubscriptionUserDetails.objects.get(user=user, is_active=True)
            
#             # Get counts filtered by subscription_user
#             total_rooms = Room.objects.filter(subscription_user=subscription_details).count()
#             active_bookings = Booking.objects.filter(
#                 subscription_user=subscription_details,
#                 status='confirmed'
#             ).count()
#             team_members = TeamMember.objects.filter(
#                 subscription_user=subscription_details
#             ).count()
            
#             # Get recent bookings for the table
#             recent_bookings = Booking.objects.filter(
#                 subscription_user=subscription_details
#             ).select_related(
#                 'guest', 'room'
#             ).order_by('-created_at')[:10]
            
#             # Calculate revenue statistics
#             revenue_data = Booking.objects.filter(
#                 subscription_user=subscription_details,
#                 status='confirmed'
#             ).aggregate(
#                 total_revenue=models.Sum('total_amount'),
#                 avg_revenue=models.Avg('total_amount'),
#                 max_revenue=models.Max('total_amount')
#             )
            
#             # Get room type distribution
#             room_types = Room.objects.filter(
#                 subscription_user=subscription_details
#             ).values('room_type').annotate(
#                 count=models.Count('id')
#             ).order_by('-count')
            
#             # Get booking status distribution
#             booking_statuses = Booking.objects.filter(
#                 subscription_user=subscription_details
#             ).values('status').annotate(
#                 count=models.Count('id')
#             ).order_by('-count')
            
#             # Get top performing rooms
#             top_rooms = Booking.objects.filter(
#                 subscription_user=subscription_details
#             ).values('room__room_number').annotate(
#                 booking_count=models.Count('id'),
#                 total_revenue=models.Sum('total_amount')
#             ).order_by('-total_revenue')[:5]
            
#             # Get logo settings
#             logo_settings = LogoSettings.objects.filter(
#                 subscription_user=subscription_details
#             ).first()
            
#             context = {
#                 'subscription': subscription_details.subscription_plan,
#                 'subscription_end_date': subscription_details.subscription_end_date,
#                 'total_rooms': total_rooms,
#                 'max_rooms': subscription_details.subscription_plan.max_rooms if subscription_details.subscription_plan else 0,
#                 'active_bookings': active_bookings,
#                 'team_members': team_members,
#                 'max_team_members': subscription_details.subscription_plan.max_team_members if subscription_details.subscription_plan else 0,
#                 'recent_bookings': recent_bookings,
#                 'total_revenue': revenue_data['total_revenue'] or 0,
#                 'avg_revenue': revenue_data['avg_revenue'] or 0,
#                 'max_revenue': revenue_data['max_revenue'] or 0,
#                 'room_types': room_types,
#                 'booking_statuses': booking_statuses,
#                 'top_rooms': top_rooms,
#                 'logo_settings': logo_settings,
#                 'company_name': subscription_details.company_name or "Your Hotel",
#                 'has_subscription': True
#             }

#         except SubscriptionUserDetails.DoesNotExist:
#             context = {
#                 'has_subscription': False,
#                 'company_name': "Your Hotel"
#             }

#         return render(request, 'hotelapp/dashboard.html', context)


@login_required  
def check_subscription_status(request):
    """Check subscription status and plan"""
    user = request.user
    subscription = SubscriptionUserDetails.objects.filter(
        user=user,
        is_active=True
    ).select_related('subscription_plan').first()
    
    if not subscription:
        return JsonResponse({
            'success': False,
            'message': 'No active subscription found',
            'has_subscription': False
        })
    
    if not subscription.subscription_plan:
        return JsonResponse({
            'success': False,
            'message': 'No subscription plan found',
            'has_subscription': True,
            'has_plan': False
        })
    
    return JsonResponse({
        'success': True,
        'message': 'Active subscription and plan found',
        'has_subscription': True,
        'has_plan': True,
        'plan_details': {
            'name': subscription.subscription_plan.name,
            'max_members': subscription.subscription_plan.max_members
        }
    })

@require_POST
def check_subscription_status(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.filter(
            user=request.user, 
            is_active=True
        ).select_related('subscription_plan').first()
        
        return JsonResponse({
            'success': True,
            'is_active': bool(subscription_user),
            'plan_name': subscription_user.subscription_plan.name if subscription_user else None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })



@login_required
def room_type_view(request):
    user = request.user  # Get the logged-in user

    # Fetch the subscription user details
    try:
        subscription = SubscriptionUserDetails.objects.get(user=user)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Subscription details not found'}, status=404)

    if request.method == "POST":
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            room_type = form.save(commit=False)
            room_type.subscription_user = subscription  # Assign subscription user correctly
            room_type.save()
            return JsonResponse({'success': True, 'message': 'Room type added successfully'})
        return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = RoomTypeForm()  # Initialize the form

    # Fetch all room types related to the user's subscription
    room_types = RoomType.objects.filter(subscription_user=subscription).values('id', 'name', 'available_from', 'room_type')

    return JsonResponse({'success': True, 'room_types': list(room_types)})

@login_required
def logo_settings_view(request):
    subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()

    if not subscription_user:
        return JsonResponse({"success": False, "error": "No subscription details found for this user."}, status=400)

    logo_settings, created = LogoSettings.objects.get_or_create(subscription_user=subscription_user)

    if request.method == 'POST':
        form = LogoSettingsForm(request.POST, request.FILES, instance=logo_settings)
        
        if form.is_valid():
            logo_settings = form.save(commit=False)
            logo_settings.subscription_user = subscription_user
            logo_settings.save()
            
            return JsonResponse({
                "success": True,
                "message": "Settings saved successfully!",
                "favicon_url": logo_settings.favicon.url if logo_settings.favicon else None,
                "light_logo_url": logo_settings.light_logo.url if logo_settings.light_logo else None,
                "dark_logo_url": logo_settings.dark_logo.url if logo_settings.dark_logo else None,
            })
        else:
            # Return form errors as string
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "error": errors}, status=400)

    return JsonResponse({"error": "Only POST allowed"}, status=405)



@login_required
@csrf_exempt  # Use this if CSRF token issues occur (not needed if AJAX sends CSRF)
def team_designation_view(request):
    """View for handling team designation submissions"""
    user = request.user  

    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=user)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({'error': 'Subscription details not found.'}, status=400)

    if request.method == "POST":
        designation = request.POST.get('teamDesignation')
        date_time = datetime.now()  # Set the current date and time directly

        # Debugging: Print received data
        print("Received Data:", designation, date_time)

        # Validate form data
        if not designation or not date_time:
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

        # Save to database
        team_designation = TeamDesignation.objects.create(
            subscription_user=subscription_user, 
            designation=designation, 
            date_time=date_time
        )

        # Debugging: Check if object is created
        print("Saved Data:", team_designation)

        return JsonResponse({
            'status': 'success',
            'message': 'Team designation saved successfully!'
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Please correct the errors in the form!',
        'errors': 'Invalid request method',
    }, status=400)
        
        


@login_required
def room_type_view(request):
    user = request.user

    # ✅ Check if user has subscription
    try:
        subscription = SubscriptionUserDetails.objects.get(user=user)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Subscription details not found!'
        }, status=404)

    # ✅ Handle POST Request
    if request.method == "POST":
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            room_type = form.save(commit=False)
            room_type.subscription_user = subscription
            room_type.save()

            # ✅ Return Success Response
            return JsonResponse({
                'success': True,
                'message': 'Room type added successfully!'
            })

        # ✅ Return Form Validation Errors
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    # ✅ Return Invalid Request Method Error
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=400)


@login_required
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            # ✅ Assign the subscription user
            subscription_user = SubscriptionUserDetails.objects.get(user=request.user)

            # ✅ Save the event
            event = form.save(commit=False)
            event.subscription_user = subscription_user
            event.save()

            # ✅ Return Success Message
            return JsonResponse({
                'success': True,
                'message': 'Event added successfully!'
            })

        # ✅ Handle Validation Error
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    # ✅ Handle Invalid Request
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)

@login_required
def ajax_guest_list(request):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    subscription_user_details = SubscriptionUserDetails.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not subscription_user_details:
        return JsonResponse({'error': 'No active subscription found for the user.'}, status=400)

    guests = Guest.objects.filter(subscription_user=subscription_user_details).prefetch_related('booking_set')

    guest_list = []
    for guest in guests:
        guest_list.append({
            'id': guest.id,
            'name': guest.name,
            'phone': guest.phone,
            'email': guest.email,
            'total_amount': sum(booking.total_amount for booking in guest.booking_set.all()) if guest.booking_set.exists() else 0
        })

    return JsonResponse({'guests': guest_list}) 

@login_required
def ajax_booking_list(request):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        logger.info("Fetching subscription details for user: %s", request.user.id)
        subscription_user_details = SubscriptionUserDetails.objects.filter(    
            user=request.user, is_active=True
        ).first()

        if not subscription_user_details:
            logger.warning("No active subscription found for user: %s", request.user.id)
            return JsonResponse({'error': 'No active subscription found for the user.'}, status=400)

        logger.info("Fetching bookings for user: %s", request.user.id)
        # Remove prefetch_related if there is no related name 'booking_set'
        bookings = Booking.objects.filter(subscription_user=subscription_user_details)

        booking_list = []
        for booking in bookings:

            room_info = f"{booking.room.room_type}-{booking.room.room_number}{booking.room.block}"  # Assuming room_number is a field in the Room model

            booking_list.append({
                'id': booking.id,
                'room_type': room_info,
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'total_amount': booking.total_amount,
                'status': 'Active' if booking.check_out > timezone.now() else 'Completed'
            })

        if not booking_list:
            logger.info("No bookings found for user: %s", request.user.id)

        logger.info("Successfully fetched bookings for user: %s", request.user.id)
        return JsonResponse({'bookings': booking_list})

    except Exception as e:
        logger.error(f"Error in ajax_booking_list: {e}", exc_info=True)  # Log the error with traceback
        return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)


@login_required
def ajax_team_list(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        subscription_user_details = SubscriptionUserDetails.objects.filter(
            user=request.user, is_active=True
        ).first()

        if not subscription_user_details:
            return JsonResponse({'error': 'No active subscription found.'}, status=400)

        team_members = TeamMember.objects.filter(subscription_user=subscription_user_details)

        team_list = []
        for member in team_members:
            team_list.append({
                'id': member.id,
                'name': member.name,
                'phone1': member.phone1,
                'email1': member.email1,
                'designation': member.designation.designation if member.designation else '—',
            })

        return JsonResponse({'team': team_list}, status=200)

    except Exception as e:
        logger.exception("Exception in ajax_team_list view")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


@login_required
def create_feature_view(request):
    """Handles feature creation via AJAX"""
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Subscription not found'}, status=400)

    if request.method == 'POST':
        feature_form = FeatureForm(request.POST, request.FILES)

        if feature_form.is_valid():
            feature = feature_form.save(commit=False)
            feature.subscription_user = subscription_user
            feature.save()

            # ✅ Return Success Response
            return JsonResponse({
                'success': True,
                'message': 'Feature added successfully!',
                'feature': {
                    'id': feature.id,
                    'name': feature.name,
                    'image': feature.image.url
                }
            }, status=200)

        # ✅ Return Validation Errors
        return JsonResponse({'success': False, 'errors': feature_form.errors.get_json_data()}, status=400)

    # ✅ Handle Invalid Request
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
@csrf_exempt
def delete_room_type(request, id):
    if request.method == 'POST':
        try:
            room_type = get_object_or_404(RoomType, id=id)
            room_type.delete()
            return JsonResponse({'status': 'success', 'message': 'Room Type deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
@csrf_exempt
def delete_team_designation(request, id):
    if request.method == 'POST':
        try:
            team_designation = get_object_or_404(TeamDesignation, id=id)
            team_designation.delete()
            return JsonResponse({'status': 'success', 'message': 'Team Designation deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
@csrf_exempt
def delete_event(request, id):
    if request.method == 'POST':
        try:
            event = get_object_or_404(Event, id=id)
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required
@csrf_exempt
def delete_feature(request, id):
    if request.method == 'POST':
        try:
            feature = get_object_or_404(Feature, id=id)
            feature.delete()
            return JsonResponse({'status': 'success', 'message': 'Feature deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# @login_required
# def fetch_bookings(request):
#     if request.method == 'GET':
#         bookings = Booking.objects.filter(user=request.user)  # Adjust the filter as needed
#         booking_data = [
#             {
#                 'id': booking.id,
#                 'room_type': booking.room.room_type,
#                 'check_in': booking.check_in,
#                 'check_out': booking.check_out,
#                 'total_amount': booking.total_amount,
#                 'status': 'Active' if booking.check_out > timezone.now() else 'Completed'
#             }
#             for booking in bookings
#         ]
#         return JsonResponse({'success': True, 'bookings': booking_data})
#     return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


class RoomListAjaxView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Get the subscription details of the logged-in user
            subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        except SubscriptionUserDetails.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Subscription not found'}, status=400)

        # Get rooms that belong to the subscription user
        rooms = Room.objects.filter(subscription_user=subscription_user, is_available=True).values(
            "room_number","block", "base_price", "ac_type", "bed_type", "max_occupancy", "room_type", "seating_capacity"
        )

        room_data = {}

        for room in rooms:
            room_type = room["room_type"]
            if room_type not in room_data:
                room_data[room_type] = {"title": f"{room_type.capitalize()} Rooms", "rooms": []}
            
            formatted_room_number = f"{room['room_number']}-{room['block']}" if room.get("block") else room["room_number"]

            # Room type condition: show bed type for regular rooms, seating capacity for conference rooms
            room_info = {
                "number": formatted_room_number,
                "price": f"₹{room['base_price']}/-",
                "ac": "AC" if room["ac_type"] == "ac" else "NON AC",
                "maxOccupancy": room["max_occupancy"],
            }

            if room_type == "conference":
                room_info["seatingCapacity"] = room["seating_capacity"]
            else:
                room_info["bedType"] = room["bed_type"]

            room_data[room_type]["rooms"].append(room_info)

        return JsonResponse(room_data)

@login_required
def index(request):
    active_subscription_id = request.session.get('active_subscription_id')

    if not active_subscription_id:
        messages.error(request, 'No active subscription found.')
        return redirect('subscription:plans')

    subscription_user = SubscriptionUserDetails.objects.filter(
        id=active_subscription_id,
        user=request.user,
        is_active=True
    ).first()

    if not subscription_user:
        messages.error(request, 'Invalid subscription.')
        return redirect('subscription:plans')

    # Basic Stats
    total_bookings = Booking.objects.filter(subscription_user=subscription_user).count()
    recent_bookings = Booking.objects.filter(subscription_user=subscription_user)

    total_revenue = Booking.objects.filter(subscription_user=subscription_user).aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_visitors = Guest.objects.filter(subscription_user=subscription_user).count()
    total_rooms = Room.objects.filter(subscription_user=subscription_user).count()
    available_rooms = Room.objects.filter(subscription_user=subscription_user, is_available=True).count()
    team_members = TeamMember.objects.filter(subscription_user=subscription_user).count()

    # Monthly Chart Data (Last 6 months)
    today = now().date()
    months = []
    revenues = []

    for i in range(5, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        month_label = f"{month_name[month_start.month]} {month_start.year}"

        month_revenue = Booking.objects.filter(
            subscription_user=subscription_user,
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        months.append(month_label)
        revenues.append(month_revenue)

    # Growth Percentages
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month.replace(day=1)
    last_month_end = last_month.replace(day=28) + timedelta(days=4)  # last day of month

    current_month_start = today.replace(day=1)

    current_month_bookings = Booking.objects.filter(
        subscription_user=subscription_user,
        created_at__gte=current_month_start).count()

    last_month_bookings = Booking.objects.filter(
        subscription_user=subscription_user,
        created_at__range=(last_month_start, last_month_end)).count()

    booking_growth = ((current_month_bookings - last_month_bookings) / last_month_bookings * 100) if last_month_bookings else 0

    current_month_revenue = Booking.objects.filter(
        subscription_user=subscription_user,
        created_at__gte=current_month_start).aggregate(total=Sum('total_amount'))['total'] or 0

    last_month_revenue = Booking.objects.filter(
        subscription_user=subscription_user,
        created_at__range=(last_month_start, last_month_end)).aggregate(total=Sum('total_amount'))['total'] or 0

    revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue else 0

    # Booking Status Breakdown
    status_labels = ['Confirmed', 'Cancelled', 'Pending']
    status_data = [
        Booking.objects.filter(subscription_user=subscription_user, status='confirmed').count(),
        Booking.objects.filter(subscription_user=subscription_user, status='cancelled').count(),
        Booking.objects.filter(subscription_user=subscription_user, status='pending').count(),
    ]

    context = {
        'total_bookings': total_bookings,
        'total_visitors': total_visitors,
        'recent_bookings': recent_bookings,

        'total_revenue': total_revenue,
        'team_members': team_members,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'rooms_availability_percent': (available_rooms / total_rooms * 100) if total_rooms else 0,
        'booking_growth': round(booking_growth, 2),
        'revenue_growth': round(revenue_growth, 2),
        'months': months,
        'revenues': revenues,
        'status_labels': status_labels,
        'status_data': status_data,
    }

    return render(request, 'hotelapp/dashboard.html', context)


@login_required
def save_facility(request):
    if request.method == "POST":
        try:
            subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()
            if not subscription_user:
                return JsonResponse({
                    "status": "error",
                    "message": "Subscription user not found. Please check your subscription."
                }, status=400)

            form = FacilityForm(request.POST, request.FILES)
            print("IMAGE file:", request.FILES.get('image'))
            print("ICON file:", request.FILES.get('icon'))
            print("IMAGE name:", getattr(request.FILES.get('image'), 'name', 'No Image'))
            print("ICON name:", getattr(request.FILES.get('icon'), 'name', 'No Icon'))
            print("IMAGE size:", getattr(request.FILES.get('image'), 'size', 'No Image'))
            print("FILES:", request.FILES)
            image = request.FILES.get('image')
            icon = request.FILES.get('icon')

            if image:
                print("Image name:", image.name)
                print("Image type:", image.content_type)
                print("Image size:", image.size)

            if icon:
                print("Icon name:", icon.name)
                print("Icon type:", icon.content_type)
                print("Icon size:", icon.size)


            if form.is_valid():
                facility = form.save(commit=False)
                facility.subscription_user = subscription_user
                facility.save()
                

                return JsonResponse({
                    "status": "success",
                    "message": "Facility has been saved successfully!"
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Please correct the form errors.",
                    "errors": form.errors
                }, status=400)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "An unexpected error occurred. Please try again.",
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method."
    }, status=400)

@login_required
@require_GET
def fetch_facilities(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        facilities = Facility.objects.filter(subscription_user=subscription_user).order_by("-id")
        data = []
        for facility in facilities:
            data.append({
                "id": facility.id,
                "name": facility.name,
                "description": facility.description,
                "image_url": facility.image.url if facility.image else "",
                "icon_url": facility.icon.url if facility.icon else "",
            })
        return JsonResponse({"status": "success", "facilities": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@require_POST
def delete_facility(request, facility_id):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        facility = Facility.objects.get(id=facility_id, subscription_user=subscription_user)
        facility.delete()
        return JsonResponse({"status": "success", "message": "Facility deleted successfully."})
    except Facility.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Facility not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def save_faq(request):
    print(f"Request method: {request.method}")  # Debug log
    print(f"POST data: {request.POST}")  # Debug log
    
    if request.method == "POST":
        try:
            question = request.POST.get('question1')
            answer = request.POST.get('answer1')

            if not question or not answer:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Question and answer are required.'
                }, status=400)

            # Get subscription user
            subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()

            # Save to database
            faq = FAQ.objects.create(
                question=question,
                answer=answer,
                subscription_user=subscription_user
            )

            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'FAQ has been saved successfully!',
                'faq_id': faq.id
            })

        except Exception as e:
            print('Error:', str(e))  # Debug log
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@login_required
@require_GET
def fetch_faqs(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        faqs = FAQ.objects.filter(subscription_user=subscription_user).order_by('-created_at')

        data = []
        for idx, faq in enumerate(faqs, start=1):
            data.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "faq_number": f"FAQ #{idx}"
            })

        return JsonResponse({"status": "success", "faqs": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@login_required
@require_POST
def delete_faq(request, faq_id):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        faq = FAQ.objects.get(id=faq_id, subscription_user=subscription_user)
        faq.delete()
        return JsonResponse({"status": "success", "message": "FAQ deleted successfully"})
    except FAQ.DoesNotExist:
        return JsonResponse({"status": "error", "message": "FAQ not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@login_required
def save_spa(request):
    if request.method == 'POST':
        try:
            # Get subscription user
            subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()

            # Get form data
            name = request.POST.get('name')
            from_time = request.POST.get('fromTime')
            to_time = request.POST.get('toTime')
            description = request.POST.get('description')
            image = request.FILES.get('image')

            # Validate required fields
            if not all([name, from_time, to_time, description,image]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required.'
                }, status=400)

            # Create spa entry
            spa = Spa.objects.create(
                name=name,
                from_time=from_time,  
                to_time=to_time,
                description=description,
                image=image,
                subscription_user=subscription_user
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Spa details saved successfully!',
                'spa_id': spa.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@login_required
@require_GET
def fetch_spa_list(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        spas = Spa.objects.filter(subscription_user=subscription_user).order_by("-created_at")

        spa_list = []
        for spa in spas:
            spa_list.append({
                "id": spa.id,
                "name": spa.name,
                "from_time": spa.from_time.strftime('%I:%M %p'),
                "to_time": spa.to_time.strftime('%I:%M %p'),
                "description": spa.description,
                "image_url": spa.image.url if spa.image else "",
            })

        return JsonResponse({"status": "success", "spas": spa_list})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@login_required
@require_POST
def delete_spa(request, spa_id):
    try:
        # Ensure user has permission to delete this SPA
        spa = Spa.objects.get(id=spa_id, subscription_user__user=request.user)
        spa.delete()
        return JsonResponse({"status": "success"})

    except Spa.DoesNotExist:
        return JsonResponse({"status": "error", "message": "SPA not found"}, status=404)

    except Exception as e:
        # Helpful logging for development
        print(f"[ERROR] Failed to delete SPA ID {spa_id}: {str(e)}")
        return JsonResponse({"status": "error", "message": "Something went wrong."}, status=500)

@login_required
def about_us_submit(request):
    if request.method == "POST":
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)

        form = AboutUsForm(request.POST, request.FILES)
        if form.is_valid():
            about_us = form.save(commit=False)
            about_us.subscription_user = subscription_user
            about_us.save()
            return JsonResponse({"success": True, "message": "About Us details saved successfully!"})
        else:
            print("form errors while submitting",form.errors)
            return JsonResponse({"success": False, "message": "Form validation failed!", "errors": form.errors})
    return JsonResponse({"success": False, "message": "Invalid request method!"})

def about_us_list(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({"status": "success", "entries": []})  # Or an error

    entries = AboutUs.objects.filter(subscription_user=subscription_user).order_by("-created_at")

    data = [
        {
            "id": entry.id,
            "title": entry.title,
            "description": entry.description,
            "image_url": entry.image.url if entry.image else "",
            "created_at": entry.created_at.strftime("%d %B %Y"),
        }
        for entry in entries
    ]

    return JsonResponse({"status": "success", "entries": data})

@login_required
@require_POST
def delete_about_us(request, entry_id):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        entry = AboutUs.objects.get(id=entry_id, subscription_user=subscription_user)
        entry.delete()
        return JsonResponse({"status": "success", "message": "About Us entry deleted."})
    except AboutUs.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Entry not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_http_methods(["POST"])
def save_service(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.filter(user=request.user).first()
        if not subscription_user:
            return JsonResponse({
                'status': 'error',
                'message': 'Subscription user not found'
            }, status=400)

        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name or not description:
            return JsonResponse({
                'status': 'error',
                'message': 'Service name and description are required'
            }, status=400)

        icon = request.FILES.get('icon')
        image = request.FILES.get('image')

        if icon and icon.size > 1024 * 1024:
            return JsonResponse({
                'status': 'error',
                'message': 'Icon file size must be less than 1MB'
            }, status=400)

        if image and image.size > 5 * 1024 * 1024:
            return JsonResponse({
                'status': 'error',
                'message': 'Image file size must be less than 5MB'
            }, status=400)

        service = Service(
            name=name,
            description=description,
            icon=icon if icon else None,
            image=image if image else None,
            subscription_user=subscription_user
        )

        # Validate before saving
        try:
            service.full_clean()  # Validates model fields
            service.save()
        except ValidationError as ve:
            return JsonResponse({
                'status': 'error',
                'message': '; '.join([f"{field}: {', '.join(errors)}" for field, errors in ve.message_dict.items()])
            }, status=400)

        return JsonResponse({
            'status': 'success',
            'message': 'Service saved successfully!',
            'service': {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'icon_url': service.icon.url if service.icon else None,
                'image_url': service.image.url if service.image else None
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }, status=500)

@login_required
@require_GET
def fetch_services(request):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        services = Service.objects.filter(subscription_user=subscription_user).order_by("-created_at")

        service_list = []
        for service in services:
            service_list.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "icon_url": service.icon.url if service.icon else "",
                "image_url": service.image.url if service.image else "",
            })

        return JsonResponse({"status": "success", "services": service_list})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@require_POST
def delete_service(request, service_id):
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
        service = Service.objects.get(id=service_id, subscription_user=subscription_user)
        service.delete()
        return JsonResponse({"status": "success", "message": "Service deleted."})
    except Service.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Service not found."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def get_contact_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({'notifications': [], 'unread_count': 0})

    messages = ContactMessage.objects.filter(subscription_user=subscription_user).order_by('-created_at')[:10]
    unread_count = ContactMessage.objects.filter(subscription_user=subscription_user, is_read=False).count()

    notifications = []
    for msg in messages:
        notifications.append({
            'sender': msg.name,
            'subject': msg.subject,
            'message': msg.message,
            'time': naturaltime(msg.created_at),
        })

    return JsonResponse({'notifications': notifications, 'unread_count': unread_count})

@csrf_exempt
@require_POST
def mark_contact_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({'status': 'no_subscription'})

    ContactMessage.objects.filter(subscription_user=subscription_user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

@csrf_exempt
@login_required
def save_map_embed(request):
    if request.method == "POST":
        embed_code = request.POST.get("embed_code", "").strip()
        try:
            sub_user = SubscriptionUserDetails.objects.get(user=request.user)
            user_map, created = UserMap.objects.get_or_create(subscription_user=sub_user)
            user_map.embed_code = embed_code
            user_map.save()
            return JsonResponse({'status': 'success', 'message': 'Map Embed Code saved successfully!'})
        except SubscriptionUserDetails.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Subscription user not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@csrf_exempt
@require_POST
def global_search(request):
    data = json.loads(request.body)
    query = data.get('query', '').strip()
    results = []

    # Get the current subscription user
    try:
        subscription_user = SubscriptionUserDetails.objects.get(user=request.user, is_active=True)
    except SubscriptionUserDetails.DoesNotExist:
        return JsonResponse({"results": []})  # No access to data if not a valid user

    # Search Rooms
    rooms = Room.objects.filter(
        Q(room_number__icontains=query) | Q(description__icontains=query),
        subscription_user=subscription_user
    )
    for room in rooms:
        results.append({
            "title": f"Room {room.room_number}",
            "url": f"/admin-panel/room/{room.id}/",
            "snippet": room.description[:80] + "..."
        })

    # Search Guests
    guests = Guest.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query),
        subscription_user=subscription_user
    )
    for guest in guests:
        results.append({
            "title": f"Guest: {guest.name}",
            "url": f"/admin-panel/guest/{guest.id}/",
            "snippet": guest.email
        })

    # Search Bookings
    bookings = Booking.objects.filter(
        Q(id__icontains=query),  # ✅ Use the actual field that exists
        subscription_user=subscription_user
    )

    for booking in bookings:
        results.append({
            "title": f"Booking #{booking.id}",  # Or f"BKG-{booking.id:04d}" for formatting
            "url": f"/admin-panel/bookings/{booking.id}/",
            "snippet": f"Booking for Room {booking.room.room_number}"
        })

    # Search Services
    services = Service.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        subscription_user=subscription_user
    )
    for service in services:
        results.append({
            "title": f"Service: {service.name}",
            "url": f"/admin-panel/services/{service.id}/",
            "snippet": service.description[:80] + "..."
        })

    return JsonResponse({"results": results})

@login_required
def guest_dashboard(request):
    try:
        guest = Guest.objects.get(user=request.user)
        bookings = Booking.objects.filter(guest=guest).order_by('-created_at')
        
        context = {
            'guest': guest,
            'bookings': bookings,
        }
        return render(request, 'hotelapp/guest_dashboard.html', context)
    except Guest.DoesNotExist:
        messages.error(request, 'Guest profile not found.')
        return redirect('home')
    


@login_required
def booking_invoice_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    guest = booking.guest
    room = booking.room
    company = booking.subscription_user  # SubscriptionUserDetails

    room_type = room.room_type
    room_image = room.image.url if room.image else ''  # Assuming Room model has image field

    context = {
        'booking': booking,
        'guest': guest,
        'company': company,
        'rooms': [room],  # If multi-room booking, pass a list
        'room_type': room_type,
        'room_image': room_image,
    }
    return render(request, 'hotelapp/invoice.html', context)


def tax_add_view(request):
    subscription_user = SubscriptionUserDetails.objects.get(user=request.user)
    taxes = HotelTax.objects.filter(subscription_user=subscription_user)  # ✅ Only non-platform taxes

    if request.method == 'POST':
        form = TaxForm(request.POST)
        if form.is_valid():
            tax = form.save(commit=False)
            tax.subscription_user = subscription_user
            tax.save()
            messages.success(request, 'Tax added successfully.')
            return redirect('admin-panel:tax_add_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaxForm()

    return render(request, 'hotelapp/tax.html', {'form': form, 'taxes': taxes,'subscription_user': subscription_user})


@csrf_exempt
def delete_tax(request):
    if request.method == 'POST':
        tax_id = request.POST.get('id')
        try:
            tax = HotelTax.objects.get(id=tax_id)
            tax.delete()
            return JsonResponse({'success': True, 'message': 'Tax deleted successfully'})
        except HotelTax.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Tax not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@require_POST
def edit_tax(request):
    tax_id = request.POST.get('id')
    name = request.POST.get('name')
    percentage = request.POST.get('percentage')

    try:
        tax = HotelTax.objects.get(id=tax_id)
        tax.name = name
        tax.percentage = percentage
        tax.save()
        return JsonResponse({'success': True, 'message': 'Tax updated successfully.'})
    except HotelTax.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tax not found.'})
