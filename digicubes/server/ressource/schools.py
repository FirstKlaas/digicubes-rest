# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import School
from .util import BasicRessource

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolsRoute(BasicRessource):
    async def on_get(self, req: Request, resp: Response):
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        schools = [school.to_dict(filter_fields) for school in await School.all()]
        resp.media = schools
