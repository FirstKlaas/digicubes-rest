"""
The endpoint for rights
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right
from .util import BasicRessource, create_ressource


logger = logging.getLogger(__name__)

class RightsRessource(BasicRessource):
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
        """
        Deletes all rights.
        """
        await Right.all().delete()

    async def on_post(self, req: Request, resp: Response):
        """
        Create new right ressource.
        """
        data = await req.media()
        resp.status_code, resp.media = await create_ressource(Right, data)
