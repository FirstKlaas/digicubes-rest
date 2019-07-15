"""
Route endpoint for roles that belong to an right.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Right
from .util import BasicRessource, needs_int_parameter, error_response


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RightRolesRessource(BasicRessource):
    """
    Route endpoint for roles, that belog ro a right.
    """

    @needs_int_parameter("right_id")
    async def on_get(self, req: Request, resp: Response, *, right_id: int):
        """
        Get all roles, that belong to the specified id. If no right
        with the given id can be found, a 404 status is send back.

        :param int right_id: The id of the right.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            resp.media = [role.unstructure(filter_fields) for role in right.roles]
            return
        except DoesNotExist:
            error_response(resp, 404, f"Right with id {right_id} not found.")

    async def on_delete(self, req: Request, resp: Response, *, right_id: int):
        """
        Removes all roles from a  right. This operation can not be undone. If the 
        right can not be found, a 404 status is send back.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            await right.roles.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"Right with id {right_id} not found.")
