# pylint: disable = C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import User
from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRolesRessource(BasicRessource):

    ALLOWED_METHODS = "GET, DELETE"
    """
    Endpoint for roles asscociated with a certain user.

    Supported verbs: ``get``, ``delete``
    """

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, current_user=None, user_id: int):
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.text = ""
            resp.headers["Allow"] = self.ALLOWED_METHODS

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, user_id: int):
        """
        Get the roles of e certain user
        """
        try:
            user = await User.get(id=user_id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            resp.media = [role.unstructure(filter_fields) for role in user.roles]
        except DoesNotExist:
            error_response(resp, 404, "User not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, user_id: int):
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.text = ""
            resp.headers["Allow"] = self.ALLOWED_METHODS

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, user_id: int):
        """
        Removes all roles from a user. This operation can not be undone. If the
        user can not be found, a 404 status is send back.
        """
        try:
            user = await User.get(id=user_id).prefetch_related("roles")
            await user.roles.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} not found.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
