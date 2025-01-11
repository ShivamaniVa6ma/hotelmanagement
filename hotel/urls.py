from django.urls import path
from . import views

app_name = 'user-panel'  # Ensure there are no trailing spaces

urlpatterns = [
    path('dashboard/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('room/', views.room, name='room'),
    path('bookings/', views.booking, name='booking'),
    path('team/', views.team, name='team'),
    path('facilities/', views.facilities, name='facilities'),
    path('faq/', views.frequently_asked_questions, name='faq'),
    path('services/', views.services, name='services'),
    path('spa/', views.spa, name='spa'),
    path('checkout/', views.checkout, name='checkout'),
    path('room-details/', views.room_details, name='room-details'),
    path('room-2/', views.room_two, name='room-2'),
    path('gallery/', views.gallery, name='gallery'),
    path('restaurant/', views.restaurant, name='restaurant'),
    path('contact-us/', views.contact_us, name='contact-us'),

    path('create-booking/', views.create_booking, name='create_booking'),
    path('booking-success/', views.booking_success, name='booking_success'),

    #path('booking/', views.booking_view, name='booking_view'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('fetch-rooms/', views.fetch_rooms, name='fetch_rooms'),

]