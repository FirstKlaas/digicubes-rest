import json
import logging
from typing import List, Optional
from digicubes.storage.models import User, Role
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions
from tortoise.fields import ManyToManyRelationManager

from .util import (
    BasicRessource, 
    error_response,
    needs_typed_parameter,
    needs_int_parameter
)

import functools

logger = logging.getLogger(__name__)

class UserRoleRoute(BasicRessource):
    """Bla Bla Bla"""
    
    @needs_int_parameter('role_id')
    @needs_int_parameter('user_id')
    async def on_get(self, req, resp, *, user_id, role_id):
        try:
            role = await Role.get(id=role_id, users__id=user_id)
            resp.media = role.to_dict()
        except DoesNotExist:
            resp.status_code = 404

    @needs_int_parameter('role_id')
    @needs_int_parameter('user_id')
    async def on_delete(self, req, resp, *, user_id, role_id):
        try:
            user = await User.get(id=user_id).prefetch_related("roles")
            role = None
            role_id = int(role_id)
            for r in user.roles:
                if r.id is role_id:
                    role = r
                    break
            if role is None:
                resp.status_code = 404
                resp.text = "Role not found"
            else:
                await user.roles.remove(role)
        except DoesNotExist:
            resp.status_code = 404
            resp.text = "User not found"

    @needs_int_parameter('role_id')
    @needs_int_parameter('user_id')
    async def on_put(self, req, resp, *, user_id, role_id):
        """
        Adding a role to a user

        Adds a role to a user. If the specified user or the
        specified user does not exist, a status code of 404
        is returned.

        :param user_id: The id of the user
        :param role_id: The id of the role you want to add to the user
        """
        try:
            user = await User.get(id=user_id)
            role = await Role.get(id=role_id)
            await user.roles.add(role)
        except DoesNotExist:
            resp.status_code = 404
            resp.text = "User not found"