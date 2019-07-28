# pylint: disable = C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right
from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRightsRessource(BasicRessource):

    ALLOWED_METHODS = "GET"

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, user_id: int) -> None:
        """
        Get all rights that are associated to this user via roles.
        The response contains an array of strings with the distinct
        names of the rights.
        """
        try:
            rights = await Right.filter(roles__users__id=1).distinct().values("name")
            resp.media = [right["name"] for right in rights]
            resp.status_code = 200
        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, str(error))

    def method_not_allowed(self, resp: Response) -> None:
        """
        Generalized 'method-not-allowed' response.
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, user_id: int) -> None:
        self.method_not_allowed(resp)

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, user_id: int) -> None:
        self.method_not_allowed(resp)

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, user_id: int) -> None:
        self.method_not_allowed(resp)
