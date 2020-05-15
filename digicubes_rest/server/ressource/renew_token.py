# pylint: disable=C0111
import logging

from responder import Request, Response

from .util import BasicRessource, needs_bearer_token, create_bearer_token, BluePrint

logger = logging.getLogger(__name__)  # pylint: disable=C0103
renew_token_blueprint = BluePrint()
route = renew_token_blueprint.route


@route("/token/")
class RenewTokenRessource(BasicRessource):
    """
    Creates a new token with the default lifespan
    """

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response):
        # pylint: disable=C0111
        assert req.state.api is not None, "No API attribute found in request state."

        try:
            user = self.current_user
            data = create_bearer_token(user.id, req.state.api.secret_key)
            resp.media = data.unstructure()

        except Exception as error:  # pylint: disable=broad-except
            logger.error("Unexpected error %s", error)
            resp.status_code = 500
            resp.text = str(error)
