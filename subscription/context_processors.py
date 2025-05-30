from hotelapp.models import Guest

def guest_context(request):
    guest = None
    if request.user.is_authenticated:
        try:
            guest = Guest.objects.get(user=request.user)
        except Guest.DoesNotExist:
            pass
    return {'guest': guest}
