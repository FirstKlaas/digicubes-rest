import json
import logging
from typing import List, Optional
from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions

from .util import BasicRessource, error_response
import functools

from .util import (
    BasicRessource, 
    error_response,
    needs_typed_parameter,
    needs_int_parameter
)

class UsersRoute(BasicRessource):
    """
    GET    : Request all users
    POST   : Create new user
    PUT    : Not implemented
    PATCH  : Not implemented
    DELETE : Forbidden (405)

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
            login = data.get("login", None)
            try:
                user = await User.create(
                    login=login,
                    email=data.get("email", None),
                    firstName=data.get("firstName", None),
                    lastName=data.get("lastName", None),
                )

                resp.media = user.to_dict()
                resp.headers['location'] = f"{req.url.scheme}://{req.url.host}:{req.url.port}{self.ressource_path}{user['id']}"
                resp.status_code = 201
            except IntegrityError:
                error_response(
                    resp, 409, f"User with login {login} already exists. Login must be unique."
                )
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
                logger.info(f"Commiting {len(new_users)} new users.")
                await transaction.commit()
            except IntegrityError as e:
                logger.error(f"Creation of {len(new_users)} new users failed. Rolling back. {e}")
                await transaction.rollback()
                error_response(resp, 409, str(e))
            except Exception as e:
                logger.error(f"Creation of {len(new_users)} new users failed. Rolling back. {e}")
                await transaction.rollback()
                error_response(resp, 400, str(e))
        else:
            resp.status_code = 400
