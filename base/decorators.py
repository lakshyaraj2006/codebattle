from functools import wraps

from django.shortcuts import redirect

def is_guest(redirect_url, *redirect_args, **redirect_kwargs):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url, *redirect_args, **redirect_kwargs)
    
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator