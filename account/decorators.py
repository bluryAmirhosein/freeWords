from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages


def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are Already Logged in!')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

