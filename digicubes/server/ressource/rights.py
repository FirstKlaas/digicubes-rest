"""
The endpoint for rights
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right
from .util import BasicRessource


logger = logging.getLogger(__name__)


class RightsRoute(BasicRessource):
    """
    Endpoint for rights
    """

    async def on_get(self, req: Request, resp: Response):
        """
        Get a list of all rights
        """
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        rights = [right.unstructure(filter_fields) for right in await Right.all()]
        resp.media = rights

    async def on_delete(self, req: Request, resp: Response):
        await Right.all().delete()
