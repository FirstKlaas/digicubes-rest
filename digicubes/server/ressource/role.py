"""
Endpoint for a single role
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Role
from .util import BasicRessource, error_response, needs_int_parameter


logger = logging.getLogger(__name__)


class RoleRoute(BasicRessource):
    """
    Endpoint for a role.

    +--------+--------------------------+
    | GET    | Get a single role        |
    +--------+--------------------------+
    + DELETE | Delete a role            |
    +--------+--------------------------+
    """

    @needs_int_parameter("role_id")
    async def on_get(self, req: Request, resp: Response, *, role_id: int):
        """
        Get the role specified by its id.

        If no role can be found with the given id, a 404 status
        code is send back.

        .. code-block:: html

            GET /roles/<role_id>


        """
        logger.debug("GET /roles/%s/", role_id)
        role = await Role.get(id=role_id)
        resp.media = role.unstructure(self.get_filter_fields(req))

    @needs_int_parameter("role_id")
    async def on_delete(self, req: Request, resp: Response, *, role_id: int):
        """
        Delete a role specified by its id.

        :param int role_id: The id of the role
        """
        try:
            role = await Role.get(id=role_id)
            await role.delete()
            resp.media = role.unstructure()
        except DoesNotExist:
            error_response(resp, 404, f"Role with id {role_id} does not exist.")
