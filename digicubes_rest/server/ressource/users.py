# pylint: disable=C0111
import logging
from typing import Dict
from responder import Request, Response

from digicubes_rest.storage import models
from .util import BasicRessource, error_response, needs_bearer_token, BluePrint, create_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
# logger.setLevel(logging.DEBUG)

users_blueprint = BluePrint()
route = users_blueprint.route


@route("/users/")
class UsersRessource(BasicRessource):
    """
    Supported verbs:
    """

    @needs_bearer_token()
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
            resp.status_code, resp.media = await models.User.create_ressource(
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

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response):
        """
        Requesting all users.
        """
        # assert req.state.api is not None, "No API attribute found in request state."

        count_users = await models.User.all().count()

        offset, limit = self.pagination(req, count_users)
        response_data = {
            "_pagination": {"count": count_users, "limit": limit, "offset": offset},
            "_links": {
                "self": f"{req.state.api.url_for(self.__class__)}?offset={offset}&limit={limit}"
            },
        }
        try:
            filter_fields = self.get_filter_fields(req)
            response_data["result"] = [
                user.unstructure(filter_fields=filter_fields, exclude_fields=["password_hash"])
                for user in await models.User.all().offset(offset).limit(limit)
            ]
            resp.media = response_data

        except ValueError as error:  # pylint: disable=W0703
            logger.exception("Could not retrieve users.", exc_info=error)
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_put(self, req, resp, current_user=None):
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.text = ""
        resp.headers["Allow"] = "POST, GET, DELETE"

    @needs_bearer_token()
    async def on_delete(self, req, resp, current_user=None):
        """
        This operation will delete every (!) user in the database.
        Even the root user. This may lead to an unusable system.

        .. warning::
            Like all the other operations, this operation is undoable. All users will
            be deleted. So think twice before calling it.

        """
        try:
            await models.User.all().delete()
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))


@route("/user/login/{operation}/{data}")
async def filter_user_by_login(req: Request, resp: Response, *, operation, data):
    # pylint: disable=unused-variable
    # TODO: This method is deprecated as it is substituted by the more
    # general get_user_by_attr method
    if req.method == "get":
        users = []
        if operation == "contains":
            users = await models.User.filter(login__contains=data)
        elif operation == "icontains":
            users = await models.User.filter(login__icontains=data)
        elif operation == "startwith":
            users = await models.User.filter(login__startswith=data)
        elif operation == "istartswith":
            users = await models.User.filter(login__istartswith=data)
        elif operation == "endswith":
            users = await models.User.filter(login__endswith=data)
        elif operation == "iendswith":
            users = await models.User.filter(login__iendswith=data)
        elif operation == "iequals":
            users = await models.User.filter(login__iequals=data)
        else:
            resp.status_code = 400
            resp.text("Unupported filter operation.")
            return

        resp.media = [user.unstructure(exclude_fields=["password_hash"]) for user in users]

    else:
        resp.status_code = 405
        resp.text = "Method not allowed"


@route("/users/filter/")
async def get_user_by_attr(req: Request, resp: Response):
    try:
        result = await users_blueprint.build_query_set(models.User, req)
        if result is None:
            resp.media = None
        elif isinstance(result, int):
            resp.media = result
        elif isinstance(result, models.User):
            resp.media = result.unstructure(exclude_fields=["password_hash"])
        else:
            resp.media = [user.unstructure(exclude_fields=["password_hash"]) for user in result]
    except:  # pylint: disable=bare-except
        logger.exception("Unable to perform filter")


@route("/user/register/")
async def register_new_user(req: Request, resp: Response):

    if req.method == "post":
        try:
            data = await req.media()
            secret = req.state.settings.secret
            resp.status_code, user_json = await models.User.create_ressource(data)
            token = create_bearer_token(user_json["id"], secret)
            resp.media = {
                "user": user_json,
                "bearer_token_data": token.unstructure(),
            }
            resp.status_code = 201
        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not register new user")
            error_response(resp, 500, str(error))
    else:
        resp.status_code = 405
        resp.headers["Allow"] = "POST"
        resp.text = f"Method {req.method} not allowed"
