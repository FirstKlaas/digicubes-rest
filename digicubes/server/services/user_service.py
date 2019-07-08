import json

from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
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

user = Blueprint('/users')

@user.route('/')
class UserRessourceA:
    async def on_get(self, req, resp):
        users = await User.all()    
        resp.media = [user.value_dict() for user in users]

    async def on_post(self, req, resp):
        data = await req.media()
        try:            
            #todo bulk create
            resp.status_code = 201
        except IntegrityError:
            resp.media = {
                'errors' : [
                    {
                        'msg' : f'User with login {login} already exists. Login must be unique.'
                    }
                ]
            }
            resp.status_code = 405

    async def on_delete(self, req, resp):
        resp.status_code = 405

@user.route('/{id}')
class UserGetOrUpdateRessource:
    def update_attribute(self, user, data):
        print(User.__public_fields__)
        print(User.__updatable_fields__)

        for attribute in User.__updatable_fields__:
            val = data.get(attribute, None)
            if val is not None:
                setattr(user, attribute, val)

    async def on_get(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            resp.json = user

        except DoesNotExist:
            resp.status_code = 404
    
    async def on_post(self, req, resp, *, id):
        resp.status_code = 500
  
    async def on_put(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            data = await req.media()
            self.update_attribute(user,data)
            await user.save()
            resp.media = user.value_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {
                'errors' : [
                    {
                        'msg' : f'User with id {id} does not exist.'
                    }
                ]
            }
        except IntegrityError as e:
            resp.status_code = 405
            resp.media = {
                'errors' : [
                    {
                        'msg' : str(e)
                    }
                ]
            }
               


@user.route('/login/{login}')
async def get_user_by_login(req, resp, *, login):
    user = await User.filter(login=login).first()
    if user is not None:
        d = user.as_dict()
        resp.media = d
    else:
        resp.text = "not found"