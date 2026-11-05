from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, _("You are not authorized to access this page."))
            return redirect('userauths:sign-in') 
        return view_func(request, *args, **kwargs)
    return wrapper
