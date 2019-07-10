import json
import logging

from digicubes.storage.models import User, Role
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError

from .util import BasicRessource, error_response
from .. import Blueprint

logger = logging.getLogger(__name__)


role = Blueprint("/roles")


@role.route("/")
class RolesRessource(BasicRessource):
    async def on_get(self, req, resp):
        logger.debug("GET /roles/")
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        roles = [role.to_dict(filter_fields) for role in await Role.all()]
        resp.media = roles

@role.route("/{id}")
class RightService(BasicRessource):
    async def on_get(self, req, resp, *, id):
        logger.debug(f"GET /roles/{id}/")
        role = await Role.get(id=id)
        resp.media = role.to_dict(self.get_filter_fields(req))