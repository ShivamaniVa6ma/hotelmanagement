def user_context(request):
    return {
        'is_authenticated': request.user.is_authenticated,
        'user': request.user if request.user.is_authenticated else None,
    } 