from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import SubscriptionUserDetails
import re

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def is_public_url(self, path):
    # Define public URL patterns that don't require subscription check
        public_url_patterns = [
            # Admin panel URLs
            r'^/admin-panel/(login|signup|forgot-password|reset-password)/$',
            r'^/admin-panel/invoice/[\w-]+/$',  # ✅ Add this for invoice detail view
            # Subscription URLs
            r'^/subscription/(plans|cart/\d+|user-details/\d+/\d+|create-payment|bloomup|payment-callback|payment-success|payment-failed|payment-cancel|create-plan|edit-plan/\d+|send-guest-otp|validate-guest-otp|cart/update-price|checkout|login|exceed|support|contact|exceed-cloud|clients|contact/submit|guest/register|fetch-pricing|upgrade/\d+|status|terms-and-condition|privacy-policy|refund-policy|invoice/[\w\-]+)/$',
            r'^/subscription/$',

            # User panel URLs with dynamic company_name
            r'^/user-panel/[^/]+/(dashboard|about|room|bookings|team|facilities|faq|services|spa|checkout|room-details|gallery|restaurant|check-availability|create-booking|booking-success|booking-failure|fetch-rooms|fetch-room-prices|fetch-seating-capacities|fetch-bed-types|get-price-estimate|fetch-room-types|payment-callback|privacy|terms-and-conditions|cancellation|contact)/$',  

            # Static and media files
            r'^/static/.*$',
            r'^/media/.*$',
            r'^/favicon\.ico$',
            r'^/robots\.txt$',
        ]

        for pattern in public_url_patterns:
            if re.match(pattern, path):
                return True
        return False


    def __call__(self, request):
        print(f"Current path: {request.path}")
        
        # Always allow access to admin
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Allow access to public URLs without any checks
        if self.is_public_url(request.path):
            print(f"Public URL access granted for: {request.path}")
            return self.get_response(request)

        # Skip subscription check for login/logout actions
        if request.method == 'POST' and request.path == '/admin-panel/login/':
            return self.get_response(request)

        # For authenticated users accessing protected URLs
        if request.user.is_authenticated:
            # Skip subscription check for logout
            if request.path == '/admin-panel/logout/':
                return self.get_response(request)

            try:
                subscription = SubscriptionUserDetails.objects.get(
                    user=request.user,
                    is_active=True
                )
                
                # Check if subscription has expired
                if subscription.subscription_end_date and subscription.subscription_end_date < timezone.now():
                    subscription.is_active = False
                    subscription.save()
                    if not request.path.startswith('/subscription/'):
                        messages.warning(request, 'Your subscription has expired. Please renew your subscription.')
                        return redirect('subscription:plans')
                
                return self.get_response(request)
                    
            except SubscriptionUserDetails.DoesNotExist:
                if not request.path.startswith('/subscription/'):
                    messages.warning(request, 'No active subscription found. Please subscribe to continue.')
                    return redirect('subscription:plans')
        
        # For non-authenticated users trying to access protected URLs
        if not request.user.is_authenticated and not self.is_public_url(request.path):
            print(f"Redirecting to login for path: {request.path}")
            return redirect('admin-panel:login')
            
        return self.get_response(request) 