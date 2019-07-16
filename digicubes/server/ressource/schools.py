# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import School
from .util import BasicRessource, create_ressource

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolsRessource(BasicRessource):
    async def on_get(self, req: Request, resp: Response):
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        schools = [school.unstructure(filter_fields) for school in await School.all()]
        resp.media = schools

    async def on_post(self, req: Request, resp: Response):
        """
        Create a new school
        """
        logger.debug("POST /schools/")
        data = await req.media()
        resp.status_code, resp.media = await create_ressource(School, data)

    async def on_delete(self, req: Request, resp: Response):
        await School.all().delete()
