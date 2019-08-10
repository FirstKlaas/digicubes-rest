# pylint: disable=C0111
import logging

from responder import Request, Response

from digicubes.common import structures as st
from .util import BasicRessource, needs_bearer_token, create_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
logger.setLevel(logging.DEBUG)


class RenewTokenRessource(BasicRessource):
    """
    Creates a new token with the default lifespan
    """

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response):
        # pylint: disable=C0111
        try:
            user = self.current_user
            token = create_bearer_token(user.id, req.api.secret_key)
            data = st.BearerTokenData(bearer_token=token, user_id=user.id)
            resp.media = data.unstructure()

        except Exception as error:  # pylint: disable=broad-except
            logger.error("Unexpected error %s", error)
            resp.status_code = 500
            resp.text = str(error)
