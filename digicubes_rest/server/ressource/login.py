"""
Endpoint for user-login
"""
import logging
from datetime import datetime

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.exceptions import BadPassword
from digicubes_rest.storage.models import User

from .util import BasicRessource, BluePrint, create_bearer_token

logger = logging.getLogger(__name__)
login_blueprint = BluePrint()
route = login_blueprint.route


@route("/login/")
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
            try:
                user = await User.get_or_none(login=login, is_verified=True, is_active=True)
                if user is None:
                    logger.debug(
                        "No user with login found %s. Or not verified or not active",
                        login,
                    )
                    resp.status_code = 401
                    resp.text = f"User with login {login} not found or wrong password."
                    return
            except Exception as error:
                logger.exception("Could not retrieve user object.")
                raise DoesNotExist(f"Could not get user {login}") from error

            # user = await User.get(login=login)
            logger.debug("Got user. Checking password")

            if not user.verify_password(password):
                logger.debug("Wrong password")
                raise BadPassword()

            # Remember the date, when the user logged in last
            user.last_login_at = datetime.utcnow()
            await user.save()

            # Create the authentication token.
            data = create_bearer_token(user.id, req.state.api.secret_key)
            data.send_json(resp)

        except BadPassword:
            logger.debug("Wrong password")
            resp.status_code = 401
            resp.text = f"User with login {login} provided wrong password."

        except DoesNotExist:
            logger.debug("No user found")
            resp.status_code = 401
            resp.text = f"User with login {login} not found or wrong password."

        except KeyError:
            resp.status_code = 400
            resp.text = "Bad formatted body content. Check the documentation"

        except Exception as error:  # pylint: disable=broad-except
            logger.error("Unexpected error %s", error)
            resp.status_code = 500
            logger.exception("Unexpected error")
            resp.text = str(error)
