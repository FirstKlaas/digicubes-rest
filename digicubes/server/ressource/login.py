"""
Endpoint for user-login
"""
import logging

from datetime import datetime
from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.common import structures as st
from digicubes.common.exceptions import BadPassword
from digicubes.storage.models import User
from .util import BasicRessource, create_bearer_token


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class LoginRessource(BasicRessource):
    """
    This is just e temporary solution.

    I guess we should support multiple methods
    to support login. What about basic authentification
    or form-based authentification.
    """

    # TODO: Rethink login procedure.

    async def on_post(self, req: Request, resp: Response):
        # pylint: disable=C0111
        try:
            data = await req.media()
            login = data["login"]
            password = data["password"]
            logger.debug("User %s tries to login with password: %s", login, password)
            user = await User.get(login=login, is_verified=True, is_active=True)
            logger.debug("Got user. Checking password")

            if not user.verify_password(password):
                logger.debug("Wrong password")
                raise BadPassword()

            user.last_login_at = datetime.utcnow()
            await user.save()
            token = create_bearer_token(user.id, req.api.secret_key)
            data = st.BearerTokenData(bearer_token=token, user_id=user.id)
            resp.media = data.unstructure()

        except BadPassword:
            logger.debug("Wrong password")
            resp.status_code = 401
            resp.text = f"User with login {login} provided wrong password."

        except DoesNotExist:
            logger.debug("No user found")
            resp.status_code = 401
            resp.text = f"User with login {login} not found or wrong password."

        except KeyError as error:
            resp.status_code = 400
            resp.text = "Bad formatted body content. Check the documentation"

        except Exception as error:  # pylint: disable=broad-except
            logger.error("Unexpected error %s", error)
            resp.status_code = 500
            logger.exception("Unexpected error")
            resp.text = str(error)
