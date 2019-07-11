import json
import logging

from digicubes.storage.models import User, School
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import BasicRessource, error_response
from .. import Blueprint

logger = logging.getLogger(__name__)

school = Blueprint("/schools")


@school.route("/")
class SchoolsRessource(BasicRessource):
    async def on_get(self, req, resp):
        logger.debug(f"GET {school.prefix}/")
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        schools = [school.to_dict(filter_fields) for school in await School.all()]
        resp.media = schools