# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import IntegrityError

from digicubes.storage.models import User

from .util import BasicRessource, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class MeRessource(BasicRessource):
    """
    Endpoint for a user
    """

    ALLOWED_METHODS = "GET, PUT"

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response):
        """
        Method not allowed. Returns a list of allowed methods in the ``Allow``
        header field.

        :param int user_id: The id of the user
        """
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.status_code = 405

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response) -> None:
        """
        Get a user

        :param int user_id: The id of the user.
        """
        try:
            user = await User.get(id=self.current_user.id)
            user_dict = user.unstructure(self.get_filter_fields(req))
            resp.media = user_dict
            self.set_timestamp(resp, user)
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response) -> None:
        """
        Updates a user. If the user does not exist, a 404 status is returned.

        :param int user_id: The id of the user
        """
        try:
            user = await User.get(self.current_user.id)
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
        except IntegrityError as error:
            error_response(resp, 405, str(error))

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response) -> None:
        """
        Method not allowed. Returns a list of allowed methods in the ``Allow``
        header field.

        :param int user_id: The id of the user
        """
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.status_code = 405
