# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes.storage.models import User
from .util import BasicRessource, error_response, needs_int_parameter

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRessource(BasicRessource):
    """
    Endpoint for a user
    """

    def update_attribute(self, user: User, data):
        # pylint: disable=R0201
        """
        Utility function
        """
        for attribute in User.__updatable_fields__:
            val = data.get(attribute, None)
            if val is not None:
                setattr(user, attribute, val)

    @needs_int_parameter("user_id")
    async def on_get(self, req: Request, resp: Response, *, user_id: int):
        """
        Get a user

        :param int user_id: The id of the user.
        """
        try:
            user = await User.get(id=user_id)
            user = user.unstructure(self.get_filter_fields(req))
            resp.media = user

        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist")

    @needs_int_parameter("user_id")
    async def on_post(self, req: Request, resp: Response, *, user_id: int):
        """
        Not supported
        """
        resp.status_code = 500

    @needs_int_parameter("user_id")
    async def on_delete(self, req: Request, resp: Response, *, user_id: int):
        """
        Deletes a user from the database.

        :param int user_id: The id of the user
        """
        try:
            user = await User.get(id=user_id)
            await user.delete()
            resp.media = user.unstructure()
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")

    @needs_int_parameter("user_id")
    async def on_put(self, req: Request, resp: Response, *, user_id: int):
        try:
            user = await User.get(id=user_id)
            data = await req.media()
            self.update_attribute(user, data)
            await user.save()
            resp.media = user.unstructure()
        except DoesNotExist:
            error_response(resp, 404, f"User with id {user_id} does not exist.")
        except IntegrityError as error:
            error_response(resp, 405, str(error))
