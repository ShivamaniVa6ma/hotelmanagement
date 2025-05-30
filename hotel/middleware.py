import logging
from django.http import Http404
from django.shortcuts import get_object_or_404
from subscription.models import SubscriptionUserDetails

logger = logging.getLogger(__name__)

class CompanyNameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define the app path prefix
        app_prefix = 'user-panel'
        path_parts = request.path.strip('/').split('/')
        logger.debug(f"Request path parts: {path_parts}")

        if len(path_parts) > 1 and path_parts[0] == app_prefix:
            company_name = path_parts[1]
            logger.debug(f"Extracted company name: {company_name}")

            try:
                # Check if the company name exists in the database
                subscription_user = get_object_or_404(SubscriptionUserDetails, company_name=company_name)
                request.subscription_user = subscription_user

                # Ensure Django gets the correct path by keeping the structure
                request.path_info = request.path  # Do not modify it for Django routing
                
            except Http404:
                logger.error(f"No SubscriptionUserDetails found for company name: {company_name}")
                raise Http404(f"No SubscriptionUserDetails found for company name: {company_name}")

        response = self.get_response(request)
        return response
