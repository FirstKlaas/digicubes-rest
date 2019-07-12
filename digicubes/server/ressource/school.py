import json
import logging

from digicubes.storage.models import User, School
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import (
    BasicRessource, 
    error_response,
    needs_typed_parameter,
    needs_int_parameter
)

logger = logging.getLogger(__name__)

class SchoolRoute(BasicRessource):
    @needs_int_parameter('id')
    async def on_get(self, req, resp, *, id):
        school = await School.get(id=id)
        resp.media = school.to_dict(self.get_filter_fields(req))
