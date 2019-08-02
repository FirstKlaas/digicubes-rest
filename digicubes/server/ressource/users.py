# pylint: disable=C0111
import logging

from responder import Request, Response

from digicubes.common.entities import RightEntity
from digicubes.storage.models import User
from .util import BasicRessource, error_response, create_ressource, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
logger.setLevel(logging.DEBUG)


class UsersRessource(BasicRessource):
    """
    Supported verbs:
    """

    @needs_bearer_token(RightEntity.CREATE_USER)
    async def on_post(self, req, resp):
        """
        Creates new user(s). The user data is defined as json object in the
        body of the request. You can create a single user or a group of users.
        When creating a bulk of users, the json object in the body has to be
        an array.

        Sample for creating a single user:

        .. code-block:: json

            {
                "login"     : "diggi",
                "email"     : "sam@diggicubes.org",
                "firstName" : "Samantha",
                "lastName"  : "Miller"
            }

        Only the ``login`` attribute is mandatory. So the smallest user definition would be:

        .. code-block:: json

            {
                "login"     : "diggi"
            }

        If you want to create multiple users, simply put user json object in an array.

        If a model constraint gets violated, a status code of 409 will be send back. In
        case of a bulk update, if any of the users violates a constraint, none of the
        users will created. This operation is atomic.

        If we do not know how to handle the json object, a status code of 400 is send
        back.
        """
        try:
            data = await req.media()
            resp.status_code, resp.media = await create_ressource(
                User, data, filter_fields=self.get_filter_fields(req)
            )

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token(RightEntity.READ_USER)
    async def on_get(self, req: Request, resp: Response, current_user=None):
        """
        Requesting all users.
        """
        # try:
        filter_fields = self.get_filter_fields(req)
        users = [user.unstructure(filter_fields) for user in await User.all()]
        resp.media = users

        # except ValueError as error:  # pylint: disable=W0703
        #    error_response(resp, 500, str(error))

    @needs_bearer_token(RightEntity.UPDATE_USER)
    async def on_put(self, req, resp, current_user=None):
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.text = ""
        resp.headers["Allow"] = "POST, GET, DELETE"

    @needs_bearer_token(RightEntity.DELETE_ALL_USER)
    async def on_delete(self, req, resp, current_user=None):
        """
        This operation will delete every (!) user in the database.
        Even the root user. This may lead to an unusable system.

        .. warning::
            Like all the other operations, this operation is undoable. All users will
            be deleted. So think twice before calling it.

        """
        try:
            await User.all().delete()
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
