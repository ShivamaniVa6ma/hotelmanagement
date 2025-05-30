from django.urls import path
from . import views

app_name = 'subscription'  # Ensure there are no trailing spaces

urlpatterns = [
    #path('', views.landing_page, name='index'),
    #path('cart/', views.about, name='cart'),
    path('plans/', views.subscription_plans, name='plans'),
    path('cart/<int:plan_id>/', views.cart_page, name='cart_page'),
    path('user-details/<int:plan_id>/<int:duration>/', views.user_details, name='user_details'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),

    path('invoice/<str:invoice_id>/', views.subscription_invoice, name='subscription_invoice'),


    path('create-plan/', views.create_plan, name='create_plan'),
    path('edit-plan/<int:pk>/', views.edit_plan, name='edit_plan'),
    path('cart/update-price/', views.update_cart_price, name='update_cart_price'),
    path('checkout/', views.checkout, name='checkout'),
    # path('login/', views.subscription_login, name='subscription_login'),
    path('', views.index_view, name='index_view'),

    path('bloomup/', views.exceed_view, name='exceed_view'),

    path('support/', views.support_view, name='support_view'),

    path('contact/', views.contact_view, name='contact_view'),

    path('exceed-cloud/', views.exceed_cloud_view, name='exceed_cloud_view'),

    path('fetch-pricing/', views.fetch_pricing, name='fetch_pricing'),

    path('upgrade/<int:subscription_user_id>/', views.upgrade_subscription, name='upgrade_subscription'),
    path('status/', views.subscription_status, name='subscription_status'),

    # path('upgrade/<int:subscription_id>/<int:new_plan_id>/', views.upgrade_subscription, name='upgrade_subscription'),

    path('clients/', views.client_view, name='clients_view'),
    path('guest/clients/', views.client_guest_view, name='guest_clients'),


    
    path('guest/register/', views.register_guest, name='guest_register'),
    path('send-guest-otp/', views.send_guest_email_otp, name='send_guest_otp'),
    path('validate-guest-otp/', views.validate_guest_email_otp, name='validate_guest_otp'),
    
    path('guest/<int:guest_id>/', views.guest_view, name='guest_view'),


    path('contact/submit/', views.contact_form_submit, name='contact_form_submit'),

    path('guest-list/', views.guest_list_view, name='guest_list_view'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('bookings/', views.BookingListView.as_view(), name='bookings_list'),
    path('super-admin/', views.superadmin_dashboard_view, name='super_admin'),

    path('notifications/', views.get_contact_notifications, name='notifications_view'),
    path('notifications/mark-read/', views.mark_contact_notifications_read, name='mark_contact_notifications_read'),

    path('tax-add/', views.tax_add_view, name='tax_add_view'),
    path('delete-tax/', views.delete_tax, name='delete_tax'),
    path('edit-tax/', views.edit_tax, name='edit_tax'),

    path('update-guest/', views.update_guest_field, name='update_guest_field'),

    path('terms-and-condition/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund, name='refund'),


]