"""
Route endpoint for roles that belong to an right.
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right

from .util import BasicRessource, needs_int_parameter


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RightRolesRoute(BasicRessource):
    """
    Route endpoint for roles, that belog ro a right.
    """

    @needs_int_parameter("right_id")
    async def on_get(self, req: Request, resp: Response, *, right_id: int):
        """
        Get all roles, that belong to the speciefied id.

        :param int right_id: The id of the right.
        """
        right = await Right.get(id=right_id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in right.roles]
