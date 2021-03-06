# pylint: disable=missing-docstring
import logging

from responder.core import Request, Response

from digicubes_rest.storage import models
from .util import BasicRessource, error_response, needs_bearer_token, BluePrint


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
            roles = [role.unstructure(filter_fields) for role in await models.Role.all()]
            resp.media = roles

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
            resp.status_code, resp.media = await models.Role.create_ressource(data)

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
