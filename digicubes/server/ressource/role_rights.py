"""
Endpoint for rights associsted to a role.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Role
from .util import BasicRessource, error_response, needs_int_parameter


logger = logging.getLogger(__name__)


class RoleRightsRessource(BasicRessource):
    """
    Endpoint for rights associsted to a role.
    """

    @needs_int_parameter("role_id")
    async def on_get(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        Get all rights associated to a role
        """
        role = await Role.get(id=role_id).prefetch_related("rights")
        filter_fields = self.get_filter_fields(req)
        resp.media = [right.unstructure(filter_fields) for right in role.rights]

    @needs_int_parameter("role_id")
    async def on_delete(self, req: Request, resp: Response, *, role_id: int):
        """
        Removes all rights from a role. This operation can not be undone. If the
        role can not be found, a 404 status is send back.
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            await role.rights.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"Role with id {role_id} not found.")

    @needs_int_parameter("role_id")
    async def on_post(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = "GET, DELETE"
        resp.text = ""

    @needs_int_parameter("role_id")
    async def on_put(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = "GET, DELETE"
        resp.text = ""