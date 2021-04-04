# pylint: disable = C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.model import UserModel

from .util import BasicRessource, BluePrint, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
me_roles_blueprint = BluePrint()
route = me_roles_blueprint.route


@route("/me/roles/")
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
            user = UserModel(id=self.current_user.id)
            roles = await user.get_roles()
            resp.media = roles.json()
            resp.status_code = 200
        except DoesNotExist:
            error_response(resp, 404, "User not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
