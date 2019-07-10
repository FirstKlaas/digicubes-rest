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


@right.route("/{id}")
class RightService(BasicRessource):
    async def on_get(self, req, resp, *, id):
        logger.debug(f"GET /rights/{id}/")
        right = await Right.get(id=id)
        resp.media = right.to_dict(self.get_filter_fields(req))

    async def on_delete(self, req, resp, *, id):
        try:
            right = await Right.get(id=id)
            await right.delete()
            resp.media = right.to_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {"errors": [{"msg": f"Right with id {id} does not exist."}]}
