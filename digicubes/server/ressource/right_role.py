import json
import logging

from digicubes.storage.models import User, Role, Right
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import (
    BasicRessource, 
    error_response,
    needs_typed_parameter,
    needs_int_parameter
)

from .. import Blueprint

logger = logging.getLogger(__name__)

def find_role(right: Right, role_id: int) -> bool:
    for role in right.roles:
        if role.id is role_id:
            return role
    return None

class RightRoleRoute(BasicRessource):
    """
    Operations on a specific role for a specific right
    """
    @needs_int_parameter('right_id')
    @needs_int_parameter('role_id')
    async def on_get(self, req, resp, *, right_id, role_id):
        """
        Returns a role that is associated with a given right

        :param int right_id: The id of the right
        :param int role_id: The id of the role that has to be assiociated with the right.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            role = find_role(right, role_id)
            if role is not None:
                filter_fields = self.get_filter_fields(req)
                resp.media = [role.to_dict(filter_fields) for role in right.roles]
                return
            
            resp.status_code = 404
            resp.text = f"No role with id '{role_id}' found for right '{right.name} [{right.id}]'."

        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"No right with id '{right_id}' found."

    @needs_int_parameter('right_id')
    @needs_int_parameter('role_id')
    def on_put(self, req, resp, *, right_id, role_id):
        resp.text = ""
