# pylint: disable=missing-docstring
import logging

from responder.core import Request, Response

from digicubes_rest.model import RoleModel
from digicubes_rest.storage import models

from .util import BasicRessource, BluePrint, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
roles_blueprint = BluePrint()
route = roles_blueprint.route


@route("/roles/")
class RolesRessource(BasicRessource):
    """
    Supported verbs for the roles ressource
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response) -> None:
        """
        Get all roles
        """
        try:
            filter_fields = self.get_filter_fields(req)
            logger.debug("Requesting %s fields.", filter_fields)
            query = models.Role.all()
            if filter_fields is not None:
                query = query.only(*filter_fields)

            RoleModel.list_model([RoleModel.from_orm(role) for role in await query]).send_json(
                resp
            )
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response) -> None:
        """
        Delet all roles
        """
        try:
            await models.Role.all().delete()

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response) -> None:
        """
        Create a new role(s)
        """
        try:
            logger.debug("POST /roles/")
            data = await req.media()
            role = await RoleModel.orm_create_from_obj(data)
            role.send_json(resp, status_code=201)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response) -> None:
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.headers["Allow"] = self.ALLOWED_METHODS
            resp.text = ""

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
