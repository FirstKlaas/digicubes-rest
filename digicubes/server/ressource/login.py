"""
Endpoint for user-login
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import User
from .util import BasicRessource, createBearerToken


logger = logging.getLogger(__name__)


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
            #password = data["password"]
            user = await User.get(login=login)
            token = createBearerToken(user.id, req.api.secret_key)
            resp.media = {"bearer-token": token, "user": user.unstructure()}

        except DoesNotExist:
            resp.status_code = 401
            resp.text = f"User with login {login} not found or wrong password."

        except KeyError as error:
            resp.status_code = 401  # TODO: Maybe better bad request?
            resp.text = "Bad formatted body content. Check the documentation"

        except Exception as error:  # pylint: disable=broad-except
            resp.status_code = 401
            resp.text = str(error)
