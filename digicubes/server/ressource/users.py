# pylint: disable=C0111
import logging
from typing import Dict
from responder import Request, Response

from digicubes.common.entities import RightEntity
from digicubes.storage.models import User
from .util import BasicRessource, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
# logger.setLevel(logging.DEBUG)


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

            resp.status_code, resp.media = await User.create_ressource(
                data, filter_fields=self.get_filter_fields(req)
            )

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    def pagination(self, req: Request, count: int) -> Dict[int, int]:  # pylint: disable=no-self-use
        """Utility method to create valid pagination information"""
        # TODO: Move to base class
        # TODO: Set the link header
        settings = req.state.settings.request
        limit = min(
            int(req.params.get("count", settings["default_count"])), int(settings["max_count"])
        )
        offset = int(req.params.get("offset", 0))
        return (offset, limit)

    @needs_bearer_token(RightEntity.READ_USER)
    async def on_get(self, req: Request, resp: Response):
        """
        Requesting all users.
        """
        count_users = await User.all().count()
        offset, limit = self.pagination(req, count_users)
        response_data = {
            "_pagination": {"count": count_users, "limit": limit, "offset": offset},
            "_links": {"self": f"{req.api.url_for(self.__class__)}?offset={offset}&limit={limit}"},
        }
        try:
            filter_fields = self.get_filter_fields(req)
            response_data["result"] = [
                user.unstructure(filter_fields)
                for user in await User.all().offset(offset).limit(limit)
            ]
            resp.media = response_data

        except ValueError as error:  # pylint: disable=W0703
            logger.exception("Could not retrieve users.")
            error_response(resp, 500, str(error))

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
