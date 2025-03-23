from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages


def redirect_if_authenticated(view_func):
    """
    A decorator to check if the user is already authenticated (logged in).
    If the user is authenticated, it redirects them to the home page with a message.
    This prevents authenticated users from accessing login or registration pages again.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is already logged in
        if request.user.is_authenticated:

            messages.info(request, 'You are Already Logged in!')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)

    return _wrapped_view

