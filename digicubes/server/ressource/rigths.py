import json
import logging

from digicubes.storage.models import User, Role, Right
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import (
    BasicRessource, 
    error_response,
    needs_typed_parameter,
    needs_int_parameter
)

from .. import Blueprint

logger = logging.getLogger(__name__)

class RightsRoute(BasicRessource):
    async def on_get(self, req, resp):
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        rights = [right.to_dict(filter_fields) for right in await Right.all()]
        resp.media = rights
