# pylint: disable = C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import User
from .util import BasicRessource, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class MeRolesRessource(BasicRessource):

    ALLOWED_METHODS = "GET"
    """
    Endpoint for roles asscociated with the current user.
    """

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response):
        """
        Get the roles of e certain user
        """
        try:
            user = await User.get(id=self.current_user.id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            resp.media = [role.unstructure(filter_fields) for role in user.roles]
        except DoesNotExist:
            error_response(resp, 404, "User not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
