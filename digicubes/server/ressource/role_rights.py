"""
Endpoint for rights associsted to a role.
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Role
from .util import BasicRessource, needs_int_parameter


logger = logging.getLogger(__name__)


class RoleRightsRessource(BasicRessource):
    """
    Endpoint for rights associsted to a role.
    """

    @needs_int_parameter("id")
    async def on_get(self, req: Request, resp: Response, *, role_id: int):
        """
        Get all rights associated to a role
        """
        role = await Role.get(id=role_id).prefetch_related("rights")
        filter_fields = self.get_filter_fields(req)
        resp.media = [right.unstructure(filter_fields) for right in role.rights]
