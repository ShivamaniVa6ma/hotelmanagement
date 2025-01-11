from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.urls import reverse
from django.shortcuts import render

# class SessionTimeoutMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Check if the user is authenticated
#         if request.user.is_authenticated:
#             # Check if the session has expired
#             last_activity = request.session.get('last_activity')
#             if last_activity:
#                 # Calculate the time since the last activity
#                 if (timezone.now() - last_activity).total_seconds() > settings.SESSION_COOKIE_AGE:
#                     # If the session has expired, log the user out
#                     from django.contrib.auth import logout
#                     logout(request)
#                     return redirect('login')  # Redirect to the login page

#             # Update the last activity time
#             request.session['last_activity'] = timezone.now()

#         response = self.get_response(request)
#         return response

class DateTimeJSONMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response is a JsonResponse
        if isinstance(response, JsonResponse):
            try:
                # Attempt to parse the content and re-encode with custom encoder
                content = json.loads(response.content)
                return JsonResponse(content, encoder=DjangoJSONEncoder, safe=isinstance(content, dict))
            except (ValueError, TypeError):
                # If parsing fails, return the original response
                return response
        return response

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        public_urls = [
            reverse('admin-panel:login'),
            reverse('admin-panel:signup'),
            '/admin/login/',
            '/static/',
            '/media/',
        ]

        # Skip authentication for static and media files
        if any(request.path.startswith(url) for url in ['/static/', '/media/']):
            return self.get_response(request)

        # Allow access to public URLs
        if any(request.path.startswith(url) for url in public_urls):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('admin-panel:login')

        return self.get_response(request)

class SuperuserPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 403:
            return render(request, 'hotelapp/403.html', status=403)
        return response
