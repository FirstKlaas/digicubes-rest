# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes_rest.model import UserModel

from .util import (BasicRessource, BluePrint, error_response,
                   needs_bearer_token, needs_int_parameter)

logger = logging.getLogger(__name__)  # pylint: disable=C0103

user_blueprint = BluePrint()
route = user_blueprint.route


@route("/user/{user_id}")
class UserRessource(BasicRessource):
    """
    Endpoint for a user
    """

    ALLOWED_METHODS = "GET, PUT, DELETE"

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, user_id: int):
        """
        Method not allowed. Returns a list of allowed methods in the ``Allow``
        header field.

        :param int user_id: The id of the user
        """
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.status_code = 405

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, user_id: int):
        """
        Get a user

        Filterfields in the request are supported.

        :param int user_id: The id of the user.
        """
        try:
            user = await UserModel.get(id=user_id)
            resp.media = self.to_json(req, user)
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, user_id: int):
        """
        Updates a user. If the user does not exist, a 404 status is returned.

        :param int user_id: The id of the user
        """
        try:
            # use   r = await User.get(id  =user_id)
            data = await req.media()
            # password = data.pop("password", None)

            user = UserModel.parse_raw(data)
            user.id = user_id
            await user.update()

            # Because password is not a standard field
            # it cannot be set via the update() method
            # and needs a special treatment. The setter
            # of the user takes care of it.
            # if password is not None:
            #    await user.set_password(password)

            resp.media = self.to_json(req, user)

        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except IntegrityError as error:
            error_response(resp, 405, str(error))

        except Exception as error:  # pylint: disable=W0703
            logger.fatal("Something went wrong", exc_info=error, stack_info=True)
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, user_id: int):
        """
        Deletes a user from the database.

        :param int user_id: The id of the user
        """
        try:
            user = await UserModel.get(id=user_id)
            await user.delete()
            resp.media = self.to_json(req, user)
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))


@route("/user/bylogin/{data}")
async def get_user_by_login(req: Request, resp: Response, *, data):
    # pylint: disable=unused-variable
    if req.method == "get":
        user = await UserModel.get(login=data)
        # user = await models.User.get_or_none(login=data)
        if user is None:
            resp.status_code = 404
            resp.text = f"User with login {data} not found."
        else:
            resp.media = user.json(exclude_none=True, exclude_unset=True)
    else:
        resp.status_code = 405
        resp.text = "Method not allowed"
