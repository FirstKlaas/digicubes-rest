# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes_rest.storage.models import User

from digicubes_rest.storage import models
from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token, BluePrint


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
            user = await User.get(id=user_id)
            user_dict = user.unstructure(
                filter_fields=self.get_filter_fields(req), exclude_fields=["password_hash"]
            )
            resp.media = user_dict
            self.set_timestamp(resp, user)
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
            user = await User.get(id=user_id)
            data = await req.media()

            # That's not the most elegant version. The two
            # attributes are write protected, so I pop
            # the two values from the data dict (if present).
            data.pop("created_at", None)
            data.pop("modified_at", None)

            password = data.pop("password", None)

            # Because password is not a standard field
            # it cannot be set via the update() method
            # and needs a special treatment. The setter
            # of the user takes care of it.
            if password is not None:
                user.password = password
            user.update(data)
            await user.save()

            filter_fields = self.get_filter_fields(req)
            data = user.unstructure(filter_fields=filter_fields, exclude_fields=["password_hash"])
            resp.media = data

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
            user = await User.get(id=user_id)
            await user.delete()
            filter_fields = self.get_filter_fields(req)
            resp.media = user.unstructure(
                filter_fields=filter_fields, exclude_fields=["password_hash"]
            )
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))


@route("/user/bylogin/{data}")
async def get_user_by_login(req: Request, resp: Response, *, data):
    # pylint: disable=unused-variable
    if req.method == "get":
        user = await models.User.get_or_none(login=data)
        if user is None:
            resp.status_code = 404
            resp.text = f"User with login {data} not found."
        else:
            resp.media = user.unstructure(exclude_fields=["password_hash"])
    else:
        resp.status_code = 405
        resp.text = "Method not allowed"
