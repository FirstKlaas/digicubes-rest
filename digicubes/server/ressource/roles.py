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

    async def on_get(self, req: Request, resp: Response):
        """
        Get all roles
        """
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        roles = [role.unstructure(filter_fields) for role in await Role.all()]
        resp.media = roles

    async def on_delete(self, req: Request, resp: Response):
        await Role.all().delete()

    async def on_post(self, req: Request, resp: Response):
        """
        Create a new role(s)
        """
        logger.debug("POST /roles/")
        data = await req.media()
        resp.status_code, resp.media = await create_ressource(Role, data)
