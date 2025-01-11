from django.urls import path
from . import views

app_name = 'admin-panel'

urlpatterns = [
    path('', views.index_view, name='index'),
    #path('bookings/', views.bookings_view, name='bookings'),
    # Room URLs
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('room/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('room/create/', views.add_room, name='room_create'),  # Corrected line
    path('get-room-price/', views.get_room_price, name='get_room_price'),

    
    # Guest URLs
    path('guests/', views.guest_list, name='guest_list'),
    path('guest/create/', views.guest_create, name='guest_create'), 

    # Team Member URLs
    path('team-members/', views.team_list, name='team_list'),
    path('team-member/create/', views.add_team_member, name='add_team_member'),
    path('team-member/edit/<int:member_id>/', views.edit_team_member, name='edit_team_member'),
    path('team-member/delete/<int:member_id>/', views.delete_team_member, name='delete_team_member'),

    

    # Booking URLs
    path('multiple-bookings/', views.multiple_bookings_create, name='multiple_bookings_create'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    #path('multiple-room-booking/', views.multiple_room_booking, name='multiple_room_booking'),
    #path('booking/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('booking/create/room/<room_id>/', views.booking_create, name='booking_create'),
    path('booking/create/<int:room_id>/', views.booking_create, name='booking_create_with_room'),

    #path('booking/create/<int:guest_id>/room/<int:room_id>/', views.booking_create, name='booking_create_with_room'),

    #path('rooms/check-availability/', views.check_availability, name='check_availability'),
    #path('check-room-availability/', views.check_room_availability, name='check_room_availability'),
    path('guest-booking/', views.guest_booking_create, name='guest_booking_create'),
    path('booking/guest/create/', views.guest_booking_create, name='guest_booking_create'),
    path('check-room-availability/', views.check_availability, name='check_availability'),


    # path('signup/', views.signup_view, name='signup'),
    # path('login/', views.login_view, name='login'),
    #path('logout/', views.admin_logout, name='logout'),
    path('invoice/', views.invoice_view, name='invoice'),
    path('menu/', views.menu_view, name='menu'),
    path('menu-add/', views.menu_add_view, name='menu-add'),
    path('orders/', views.orders_view, name='orders'),
    # path('forgot/', views.forgot_view, name='forgot'),
    # path('reset-password/', views.reset_password_view, name='reset-password'),
    
    path('role/', views.role_view, name='role'),
    #path('guest-details/', guest_details_view, name='guest_details'),

    path('add-food/', views.add_food_item, name='add_food_item'),
    #path('menu-add/', views.add_food_item, name='menu-add'),
    path('lunch-section/', views.lunch_section, name='lunchsection'),
    path('dinner-section/', views.dinner_section, name='dinnersection'),
    path('breakfast-section/', views.breakfast_section, name='breakfastsection'),

    #path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.register, name='signup'),

    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('booking/<int:booking_id>/view/', views.booking_detail, name='booking_view'),

    path('document/<str:doc_type>/<int:member_id>/', views.view_document, name='view_document'),

    #path('room/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('room/<int:room_id>/delete/', views.delete_room, name='delete_room'),

    path('guest/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('guest/<int:guest_id>/delete/', views.delete_guest, name='delete_guest'),

    path('rooms/<int:room_id>/edit/', views.edit_room, name='room_edit'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='room_delete'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
]   