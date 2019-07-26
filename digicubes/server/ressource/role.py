"""
Endpoint for a single role
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Role
from .util import BasicRessource, error_response, needs_int_parameter


logger = logging.getLogger(__name__)


class RoleRessource(BasicRessource):
    """
    Endpoint for a role.
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
        self.set_timestamp(resp, role)

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

    @needs_int_parameter("role_id")
    async def on_post(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = "GET, PUT, DELETE"
        resp.text = ""

    @needs_int_parameter("role_id")
    async def on_put(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        Updates the role
        """
        data = await req.media()
        # TODO: check if type is dict
        try:
            role = await Role.get(id=role_id)
            role.update(data)
            await role.save()
            resp.media = role.unstructure()  # TODO: Maybe filter on fields from header
            resp.status_code = 200

        except DoesNotExist:
            error_response(resp, 404, f"No role with id {role_id} found.")
