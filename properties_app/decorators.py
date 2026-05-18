from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    """Decorator for views that checks whether a user has a particular role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                if hasattr(request.user, 'profile') and request.user.profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('home')
        return wrap
    return decorator
