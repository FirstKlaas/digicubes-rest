import json
import logging

from digicubes.storage.models import User, Role, Right
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import BasicRessource, error_response
from .. import Blueprint

logger = logging.getLogger(__name__)


right = Blueprint("/rights")

@right.route("/")
class RolesRessource(BasicRessource):
    async def on_get(self, req, resp):
        logger.debug("GET /rights/")
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        rights = [right.to_dict(filter_fields) for right in await Right.all()]
        resp.media = rights

