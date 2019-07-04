import json

from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist
from .. import Blueprint
import functools

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

user = Blueprint('/user')

@user.route('/')
@needs_apikey()
async def user_index(req, resp: Response):
    users = await User.all()    
    resp.media = [user.value_dict() for user in users]
    
@user.route('/id/{id}')
async def get_user(req, resp: Response, *, id):
    try:
        user = await User.get(id=id)
        resp.json = user

    except DoesNotExist:
        resp.status_code = 404

@user.route('/login/{login}')
async def get_user_by_login(req, resp, *, login):
    user = await User.filter(login=login).first()
    if user is not None:
        d = user.as_dict()
        resp.media = d
    else:
        resp.text = "not found"