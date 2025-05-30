from django.urls import path
from . import views


app_name = 'admin-panel'

urlpatterns = [
    path('', views.index, name='index'),  # ✅ Use .as_view()
    #path('bookings/', views.bookings_view, name='bookings'),
    # Room URLs
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('room/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('room/create/', views.add_room, name='room_create'),  # Corrected line
    path('room/fetch-room-data/', views.fetch_room_data, name='fetch_room_data'),
    # path('room/fetch-room-details/', views.fetch_room_details, name='fetch_room_details'),

    
    
    path('invoice-list/', views.invoice_list_view, name='invoice_list'),
    path('invoice/<str:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    
    # Guest URLs
    path('guests/', views.guest_list, name='guest_list'),
    path('guest/create/', views.guest_register, name='guest_create'), 

    # Team Member URLs
    path('team-members/', views.team_list, name='team_list'),
    path('team-member/create/', views.add_team_member, name='add_team_member'),
    path('team-member/edit/<int:member_id>/', views.edit_team_member, name='edit_team_member'),
    path('team-member/<int:id>/delete/', views.delete_team_member, name='delete_team_member'),

    # Booking URLs
    path('multiple-bookings/', views.multiple_bookings_create, name='multiple_bookings_create'),
    path("get-room-types/", views.get_room_types, name="get-room-types"),
    path("get-room-type/<int:room_type_id>/", views.get_room_bed_type, name="get-room-bed-type"),  # ✅ Get a specific room type
    path("get-room-availability/", views.get_room_availability, name="get-room-availability"),  # ✅ Correct URL
    path('get-seating-capacities/', views.get_seating_capacities, name='get_seating_capacities'),


    path("get-room-price/", views.get_room_price, name="get-room-price"),  # ✅ Correct URL
    path("api/rooms/", views.RoomListAjaxView.as_view(), name="room_list_ajax"),


    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    #path('multiple-room-booking/', views.multiple_room_booking, name='multiple_room_booking'),
    #path('booking/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('booking/create/room/<room_id>/', views.booking_create, name='booking_create'),
    path('booking/create/<int:room_id>/', views.booking_create, name='booking_create_with_room'),
    path('guest/dashboard/', views.guest_dashboard, name='guest_dashboard'),

    #path('booking/create/<int:guest_id>/room/<int:room_id>/', views.booking_create, name='booking_create_with_room'),

    #path('rooms/check-availability/', views.check_availability, name='check_availability'),
    #path('check-room-availability/', views.check_room_availability, name='check_room_availability'),
    path('guest-booking/', views.guest_booking_create, name='guest_booking_create'),
    path('booking/guest/create/', views.guest_booking_create, name='guest_booking_create'),
    path('check-room-availability/', views.check_availability, name='check_availability'),


    # path('signup/', views.signup_view, name='signup'),
    # path('login/', views.login_view, name='login'),
    #path('logout/', views.admin_logout, name='logout'),
    #path('invoice/guest/<int:guest_id>/date/<str:booking_date>/', views.invoice_view, name='booking_invoice'),

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
    path('rooms/<int:room_id>/edit/', views.edit_room, name='room_edit'),
    path('room/<int:room_id>/delete/', views.delete_room, name='delete_room'),

    path('guest/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('guest/<int:id>/delete/', views.delete_guest, name='delete_guest'),

    # path('rooms/<int:room_id>/delete/', views.delete_room, name='room_delete'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    path('check-subscription/', views.check_subscription_status, name='check_subscription'),
    path('select-subscription/', views.select_subscription, name='select_subscription'),

    path('settings/', views.settings_view, name='settings_view'),

    path('settings-room-type/', views.room_type_view, name='room_type'),

    path('logo-settings/', views.logo_settings_view, name='logo_settings_view'),

    path('team-designation-settings/', views.team_designation_view, name='team_designation'),

    # settingsurl
    path('settings/guest-list/', views.ajax_guest_list, name='ajax_guest_list'),
    path('settings/team-list/', views.ajax_team_list, name='ajax_team_list'),
    path('settings/booking-list/', views.ajax_booking_list, name='ajax_booking_list'),


    path('create-event/', views.create_event_view, name='create_event'),
    #path('settings/events/', views.list_events_view, name='events'),
    path('features/create/', views.create_feature_view, name='create_feature'),

    #path('team-designation/<int:id>/edit/', views.edit_team_designation, name='edit_team_designation'),
    path('room-type/<int:id>/delete/', views.delete_room_type, name='delete_room_type'),
    path('team-designation/<int:id>/delete/', views.delete_team_designation, name='delete_team_designation'),
    path('event/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('feature/<int:id>/delete/', views.delete_feature, name='delete_feature'),

    # path('fetch-bookings/', views.fetch_bookings, name='fetch_bookings'),

    path("save-facility/", views.save_facility, name="save_facility"),
    path('facilities/fetch/', views.fetch_facilities, name='fetch_facilities'),
    path('facilities/<int:facility_id>/delete/', views.delete_facility, name='delete_facility'),

    path('save-faq/', views.save_faq, name='save_faq'),
    path('faq/fetch/', views.fetch_faqs, name='fetch_faqs'),
    path('faq/<int:faq_id>/delete/', views.delete_faq, name='delete_faq'),

    path('save-spa/', views.save_spa, name='save_spa'),
    path('spa/list/', views.fetch_spa_list, name='fetch_spa_list'),
    path('spa/<int:spa_id>/delete/', views.delete_spa, name='delete_spa'),

    path('save-about-us/', views.about_us_submit, name='about_us_submit'),
    path('about-us/list/', views.about_us_list, name='about_us_list'),
    path('about-us/<int:entry_id>/delete/', views.delete_about_us, name='delete_about_us'),

    path('save-service/', views.save_service, name='save-service'),
    path('services/list/', views.fetch_services, name='fetch_services'),
    path('services/<int:service_id>/delete/', views.delete_service, name='delete_service'),

    path('notifications/', views.get_contact_notifications, name='get_contact_notifications'),
    path('notifications/mark-read/', views.mark_contact_notifications_read, name='mark_contact_notifications_read'),


    path('save-map-embed/', views.save_map_embed, name='save_map_embed'),



    path("search/", views.global_search, name="global_search"),


    path('tax-add/', views.tax_add_view, name='tax_add_view'),
    path('delete-tax/', views.delete_tax, name='delete_tax'),
    path('edit-tax/', views.edit_tax, name='edit_tax'),

]   