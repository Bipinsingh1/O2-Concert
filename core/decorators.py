from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Restrict view to staff/superuser only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_active or not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def registered_user_required(view_func):
    """Restrict view to registered (non-guest) users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper
