# pylint: disable=C0111
import logging

from responder import Request, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes.common.entities import RightEntity
from digicubes.common import structures as st
from digicubes.storage.models import User
from .util import BasicRessource, error_response, needs_bearer_token, needs_int_parameter

logger = logging.getLogger(__name__)  # pylint: disable=C0103
# logger.setLevel(logging.DEBUG)


class PasswordRessource(BasicRessource):
    """
    Setting a users password
    """

    @needs_int_parameter("user_id")
    @needs_bearer_token(RightEntity.ROOT_RIGHT)
    async def on_post(self, req: Request, resp: Response, *, user_id: int):
        """
        Setting a password directly
        """
        try:
            data = await req.media()
            password = data["password"]
            user = await User.get(id=user_id)
            user.password = password
            await user.save()
            resp.status_code = 200
            resp_data = st.PasswordData(
                user_id=user.id, user_login=user.login, password_hash=user.password_hash
            )
            resp.media = resp_data.unstructure()

        except KeyError:
            error_response(resp, 405, "Invalid data")

        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except IntegrityError as error:
            error_response(resp, 405, str(error))

        except Exception as error:  # pylint: disable=W0703
            logger.debug("Error: %s", error)
            error_response(resp, 500, str(error))
