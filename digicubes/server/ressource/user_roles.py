# pylint: disable = C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import User
from .util import BasicRessource, needs_int_parameter

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRolesRoute(BasicRessource):
    """
    Endpoint for roles asscociated with a certain user.

    Supported verbs: ``get``
    """

    @needs_int_parameter("user_id")
    async def on_get(self, req: Request, resp: Response, *, user_id: int):
        """
        Get the roles of e certain user
        """
        user = await User.get(id=user_id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in user.roles]
