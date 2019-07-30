# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes.storage.models import User
from digicubes.common.entities import RightEntity

from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRessource(BasicRessource):
    """
    Endpoint for a user
    """

    ALLOWED_METHODS = "GET, PUT, DELETE"

    @needs_int_parameter("user_id")
    @needs_bearer_token(RightEntity.CREATE_USER)
    async def on_post(self, req: Request, resp: Response, *, current_user=None, user_id: int):
        """
        Method not allowed. Returns a list of allowed methods in the ``Allow``
        header field.

        :param int user_id: The id of the user
        """
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.status_code = 405

    @needs_int_parameter("user_id")
    @needs_bearer_token(RightEntity.READ_USER)
    async def on_get(self, req: Request, resp: Response, *, current_user=None, user_id: int):
        """
        Get a user

        :param int user_id: The id of the user.
        """
        try:
            user = await User.get(id=user_id)
            user_dict = user.unstructure(self.get_filter_fields(req))
            resp.media = user_dict
            self.set_timestamp(resp, user)
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token(RightEntity.UPDATE_USER)
    async def on_put(self, req: Request, resp: Response, *, current_user=None, user_id: int):
        """
        Updates a user. If the user does not exist, a 404 status is returned.

        :param int user_id: The id of the user
        """
        try:
            user = await User.get(id=user_id)
            data = await req.media()
            password = data.get("password", None)

            # Because password is not a standard field
            # it cannot be set via the update() method
            # and needs a special treatment. The setter
            # of the user takes care of it.
            if password is not None:
                user.password = data.pop("password")
            user.update(data)
            await user.save()
            filter_fields = self.get_filter_fields(req)
            resp.media = user.unstructure(filter_fields)
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except IntegrityError as error:
            error_response(resp, 405, str(error))

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("user_id")
    @needs_bearer_token(RightEntity.DELETE_USER)
    async def on_delete(self, req: Request, resp: Response, *, current_user=None, user_id: int):
        """
        Deletes a user from the database.

        :param int user_id: The id of the user
        """
        try:
            user = await User.get(id=user_id)
            await user.delete()
            filter_fields = self.get_filter_fields(req)
            resp.media = user.unstructure(filter_fields)
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
