import json
import logging

from digicubes.storage.models import User, Role, Right
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import BasicRessource, error_response, needs_typed_parameter, needs_int_parameter

from .. import Blueprint

logger = logging.getLogger(__name__)


class RightRolesRessource(BasicRessource):
    """
    Operation on the roles of a given right.

    Supported verbs are: :code:`GET`, :code:`DELETE`
    """

    @needs_int_parameter("id")
    async def on_get(self, req, resp, *, id):
        """
        Get all routes associated with this right.
        """
        right = await Right.get(id=id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in right.roles]

    @needs_int_parameter("id")
    async def on_delete(self, req, resp, *, id):
        """
        Removes all roles from the list of asscociated roles from the right.
        """
        try:
            right = await Right.get(id=id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            await right.roles.clear()
            resp.media = [role.to_dict(filter_fields) for role in right.roles]
        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"Right with id {id} does not exist."
