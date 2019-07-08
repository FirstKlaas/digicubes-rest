import functools

from .user_service import user as UserService

def needs_apikey():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(req, resp, *args, **kwargs):
            #apikey = req.headers.get('digicubes-apikey', None)
            #if apikey is None:
            #    resp.status_code = 500
            #    return
            print(req.method)
            await func(req, resp, *args, **kwargs)
        return wrapper
    return decorator

def needs_valid_token():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(req, resp, *args, **kwargs):
            #apikey = req.headers.get('digicubes-apikey', None)
            #if apikey is None:
            #    resp.status_code = 500
            #    return
            await func(req, resp, *args, **kwargs)
        return wrapper
    return decorator