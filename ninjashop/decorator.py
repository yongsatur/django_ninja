from functools import wraps
from django.http import HttpResponse


def check_permission(permission_codename: str, use_auth: bool = True, raise_exception: bool = True):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user_obj = request.auth if use_auth else request.user
            
            if user_obj and user_obj.has_perm(permission_codename):
                return view_func(request, *args, **kwargs)
            
            if raise_exception:
                return HttpResponse('У вас недостаточно прав для совершения данной операции!', status = 403)
            return HttpResponse('Требуется авторизация!', status = 401)
        return wrapped_view
    return decorator