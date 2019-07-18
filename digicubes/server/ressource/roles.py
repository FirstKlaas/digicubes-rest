# pylint: disable=missing-docstring
import logging

from responder.core import Request, Response

from digicubes.storage.models import Role
from .util import BasicRessource, create_ressource


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RolesRessource(BasicRessource):
    """
    Supported verbs for the roles ressource
    """

    async def on_get(self, req: Request, resp: Response) -> None:
        """
        Get all roles
        """
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        roles = [role.unstructure(filter_fields) for role in await Role.all()]
        resp.media = roles

    async def on_delete(self, req: Request, resp: Response) -> None:
        """
        Delet all roles
        """
        await Role.all().delete()

    async def on_post(self, req: Request, resp: Response) -> None:
        """
        Create a new role(s)
        """
        logger.debug("POST /roles/")
        data = await req.media()
        resp.status_code, resp.media = await create_ressource(Role, data)

    async def on_put(self, req: Request, resp: Response) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = "POST, GET, DELETE"
        resp.text = ""
