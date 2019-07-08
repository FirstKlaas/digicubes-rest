import json
import logging

from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions

from .. import Blueprint
import functools

logger = logging.getLogger("service.user")



class BasicRessource:

    X_FILTER_FIELDS = 'x-filter-fields'

    @property
    def route(self):
        return getattr(self, 'route', None)

    @property
    def prefix(self):
        return getattr(self, 'prefix', None)

    @property
    def ressource_path(self):
        return self.prefix + self.route

    def get_filter_fields(self, req):
        x_filter_fields = req.headers.get(BasicRessource.X_FILTER_FIELDS,None)
        logger.warn(f"x_filter_fields: {x_filter_fields}")
        if x_filter_fields is not None:
            fields = x_filter_fields.split(',')
            if 'id' not in fields:
                fields.append('id')
            logger.warn(f"filter_fields: {fields}")
            return fields

        return None



def error_response(resp, code, text):
    resp.media = {'errors' : [{'msg' : text}]}
    resp.status_code = code

user = Blueprint('/users')

@user.route('/')
class UsersRessource(BasicRessource):
    """
    GET    : Request all users
    POST   : Create new user
    PUT    : Not implemented
    PATCH  : Not implemented
    DELETE : Formidden (405)

    Links for the ressources are generated. To avoid the generation
    of links, add an header field 'x-hateoa' with value 'false',
    """
    async def on_get(self, req, resp):
        """
        Requesting all users.
        if the header field 'X-HATEOAS' is available, hyperlinks for
        the ressources in the respond will be generated.

        Possible values for the header field:

        self: only the link to get the ressouce will be generated
        """
        filter_fields = self.get_filter_fields(req)
        users = [user.to_dict(filter_fields) for user in await User.all()]

        # See if we are kindly asked to generate the hyperlinks
        # for the ressources
        hateoa = (req.headers.get('x-hateoa', 'true') == 'true')
        if hateoa:
            for user in users:
                user['links'] = [
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}{user['id']}",
                        'action' : 'GET',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}{user['id']}",
                        'action' : 'PUT',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}{user['id']}",
                        'action' : 'DELETE',
                        'types' : []
                    },
                    { 
                        'rel'   : 'users',
                        'href'  : f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}",
                        'action': 'GET',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'   : 'roles',
                        'href'  : f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}{user['id']}/roles/",
                        'action': 'GET',
                        'types' : ['application/json']
                    }                    
                ]
        
        resp.media = users

    async def on_post(self, req, resp):
        #
        # POST
        #
        # Creating new Ressources
        #
        data = await req.media()
        logger.info(f"Requested url is: {req.url}")
        if isinstance(data, dict):
            #
            # Try to insert a single user ressource
            #  
            login = data.get('login', None)
            try:
                user = await User.create(
                    login = login,
                    email = data.get('email', None),
                    firstName = data.get('firstName', None),
                    lastName = data.get('lastName', None)
                )
            
                resp.media = user.to_dict()
                resp.status_code = 201
            except IntegrityError:
                error_response(resp, 409, f'User with login {login} already exists. Login must be unique.')
            except Exception as e:
                error_response(resp, 400, str(e))
        elif isinstance(data, list):
            #
            # Bulk creation of many user ressources
            #
            transaction = await transactions.start_transaction()
            try:
                new_users = [User.from_dict(item) for item in data]
                # TODO: Is there a limit of how many users can be created in a single call?
                await User.bulk_create(new_users)
                logger.info(f'Commiting {len(new_users)} new users.')
                await transaction.commit()
            except IntegrityError as e:
                logger.error(f'Creation of {len(new_users)} new users failed. Rolling back. {e}')
                await transaction.rollback()
                error_response(resp, 400, str(e))
            except Exception as e:
                logger.error(f'Creation of {len(new_users)} new users failed. Rolling back. {e}')
                await transaction.rollback()
                error_response(resp, 400, str(e))
        else:
            resp.status_code = 400
            resp.media

    async def on_delete(self, req, resp):
        resp.status_code = 405

@user.route('/{id}')
class UserRessource(BasicRessource):
    def update_attribute(self, user, data):
        for attribute in User.__updatable_fields__:
            val = data.get(attribute, None)
            if val is not None:
                setattr(user, attribute, val)
            
    async def on_get(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            user = user.to_dict(self.get_filter_fields(req))

            # See if we are kindly asked to generate the hyperlinks
            # for the ressource
            hateoa = (req.headers.get('x-hateoa', 'true') == 'true')
            if hateoa:
                user['links'] = [
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}",
                        'action' : 'GET',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}",
                        'action' : 'PUT',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'    : 'self',
                        'href'   : f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}",
                        'action' : 'DELETE',
                        'types' : []
                    },
                    { 
                        'rel'   : 'users',
                        'href'  : f"{req.url.scheme}://{req.url.host}:{req.url.port}/users/",
                        'action': 'GET',
                        'types' : ['application/json']
                    },
                    { 
                        'rel'   : 'roles',
                        'href'  : f"{req.url.scheme}://{req.url.host}:{req.url.port}/users/{id}/roles/",
                        'action': 'GET',
                        'types' : ['application/json']
                    }

                ]
        
            
            resp.media = user

        except DoesNotExist:
            error_response(resp, 404, f"User with id {id} does not exist")
    
    async def on_post(self, req, resp, *, id):
        resp.status_code = 500

    async def on_delete(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            await user.delete()
            resp.media = user.to_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {
                'errors' : [
                    {
                        'msg' : f'User with id {id} does not exist.'
                    }
                ]
            }
        
    async def on_put(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            data = await req.media()
            self.update_attribute(user,data)
            await user.save()
            resp.media = user.to_dict()
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
               


@user.route("/{id}/roles/")
@user.route("/{id}/roles")
class UserRolesRessource(BasicRessource):

    async def on_get(self, req, resp, *, id):
        user = await User.get(id=id).prefetch_related('roles')
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in user.roles]
