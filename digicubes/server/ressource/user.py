import json
import logging
from typing import List, Optional
from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions

from .util import BasicRessource, error_response, needs_typed_parameter, needs_int_parameter

import functools

logger = logging.getLogger(__name__)


class UserRoute(BasicRessource):
    def update_attribute(self, user, data):
        for attribute in User.__updatable_fields__:
            val = data.get(attribute, None)
            if val is not None:
                setattr(user, attribute, val)

    @needs_int_parameter("id")
    async def on_get(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            user = user.to_dict(self.get_filter_fields(req))
            resp.media = user

        except DoesNotExist:
            error_response(resp, 404, f"User with id {id} does not exist")

    @needs_int_parameter("id")
    async def on_post(self, req, resp, *, id):
        resp.status_code = 500

    @needs_int_parameter("id")
    async def on_delete(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            await user.delete()
            resp.media = user.to_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {"errors": [{"msg": f"User with id {id} does not exist."}]}

    @needs_int_parameter("id")
    async def on_put(self, req, resp, *, id):
        try:
            user = await User.get(id=id)
            data = await req.media()
            self.update_attribute(user, data)
            await user.save()
            resp.media = user.to_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {"errors": [{"msg": f"User with id {id} does not exist."}]}
        except IntegrityError as e:
            resp.status_code = 405
            resp.media = {"errors": [{"msg": str(e)}]}
