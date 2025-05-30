from django.urls import path
from . import views

app_name = 'user-panel'  # Ensure there are no trailing spaces

urlpatterns = [
    # path('company/<str:company_name>/', views.company_detail, name='company_detail'),

    path('<str:company_name>/dashboard/', views.index, name='index'),
    path('<str:company_name>/about/', views.about, name='about'),
    #path('<str:company_name>/contact/', views.contact, name='contact'),
    path('<str:company_name>/room/', views.room, name='room'),
    path('<str:company_name>/bookings/', views.booking, name='booking'),
    path('<str:company_name>/team/', views.team, name='team'),
    path('<str:company_name>/facilities/', views.facilities_view, name='facilities'),
    path('<str:company_name>/faq/', views.frequently_asked_questions, name='faq'),
    path('<str:company_name>/services/', views.services, name='services'),
    path('<str:company_name>/spa/', views.spa, name='spa'),
    path('<str:company_name>/checkout/', views.checkout, name='checkout'),
    path('<str:company_name>/room-details/', views.room_details, name='room-details'),
    # path('<str:company_name>/room-2/', views.room_two, name='room-2'),
    path('<str:company_name>/gallery/', views.gallery, name='gallery'),
    path('<str:company_name>/restaurant/', views.restaurant, name='restaurant'),
    #path('<str:company_name>/contact-us/', views.contact_us, name='contact-us'),

    path('<str:company_name>/check-availability/', views.check_availability, name='check_availability'),

    path('<str:company_name>/create-booking/', views.create_booking, name='create_booking'),
    path('<str:company_name>/booking-success/', views.booking_success, name='booking_success'),
    path('<str:company_name>/booking-failure/', views.booking_failed, name='booking_failed'),

    #path('booking/', views.booking_view, name='booking_view'),
    path('<str:company_name>/fetch-rooms/', views.fetch_rooms, name='fetch_rooms'),
    path('<str:company_name>/fetch-room-prices/', views.fetch_room_prices, name='fetch_room_prices'),
    path('<str:company_name>/fetch-seating-capacities/', views.fetch_seating_capacities, name='fetch_seating_capacities'),
    path('<str:company_name>/fetch-bed-types/', views.fetch_bed_types, name='fetch_bed_types'),

    path('<str:company_name>/get-price-estimate/', views.get_price_estimate, name='get_price_estimate'),

    path('<str:company_name>/fetch-room-types/', views.fetch_room_types, name='fetch_room_types'),

    path('<str:company_name>/payment-callback/', views.payment_callback, name='payment_callback'),


    path('<str:company_name>/privacy/', views.privacy, name='privacy'),

    path('<str:company_name>/terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('<str:company_name>/cancellation/', views.cancellation, name='cancellation'),

    path('<str:company_name>/contact/', views.contact_view, name='contact-us'),


]