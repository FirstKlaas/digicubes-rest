import json
import logging

from digicubes.storage.models import User, School
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import BasicRessource, error_response, needs_typed_parameter, needs_int_parameter

logger = logging.getLogger(__name__)


class SchoolsRessource(BasicRessource):
    async def on_get(self, req, resp):
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        schools = [school.to_dict(filter_fields) for school in await School.all()]
        resp.media = schools
