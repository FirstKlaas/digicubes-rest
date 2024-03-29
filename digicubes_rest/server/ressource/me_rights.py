# pylint: disable = C0111
import logging

from responder.core import Request, Response

from .util import (BasicRessource, BluePrint, error_response, get_user_rights,
                   needs_bearer_token)

logger = logging.getLogger(__name__)  # pylint: disable=C0103
me_rights_blueprint = BluePrint()
route = me_rights_blueprint.route


@route("/me/rights/")
class MeRightsRessource(BasicRessource):

    ALLOWED_METHODS = "GET"

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response) -> None:
        """
        Get all rights that are associated to this user via roles.
        The response contains an array of strings with the distinct
        names of the rights.
        """
        try:
            resp.media = await get_user_rights(self.current_user)
            resp.status_code = 200
        except Exception as error:  # pylint: disable=broad-except
            logger.exception(
                "Error occurred requesting rights for current user.%s",
                self.current_user,
                exc_info=error,
                stack_info=True,
            )
            error_response(resp, 500, str(error))
