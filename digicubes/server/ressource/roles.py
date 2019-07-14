# pylint: disable=missing-docstring
import logging

from responder.core import Request, Response

from digicubes.storage.models import Role
from .util import BasicRessource


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RolesRoute(BasicRessource):
    """
    Supported verbs for the roles ressource
    """

    async def on_get(self, req: Request, resp: Response):
        """
        Get all roles
        """
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        roles = [role.to_dict(filter_fields) for role in await Role.all()]
        resp.media = roles
