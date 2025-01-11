from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from functools import wraps

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'hotelapp/403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view 