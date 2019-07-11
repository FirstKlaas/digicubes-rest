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
class RoleService(BasicRessource):
    async def on_get(self, req, resp, *, id):
        logger.debug(f"GET /roles/{id}/")
        role = await Role.get(id=id)
        resp.media = role.to_dict(self.get_filter_fields(req))

    async def on_delete(self, req, resp, *, id):
        try:
            role = await Role.get(id=id)
            await role.delete()
            resp.media = role.to_dict()
        except DoesNotExist:
            resp.status_code = 404
            resp.media = {"errors": [{"msg": f"Role with id {id} does not exist."}]}

@role.route("/{id}/rigths/")
class RoleRigthsService(BasicRessource):
    async def on_get(self, req, resp, *, id):
        role = await Role.get(id=id).prefetch_related("rights")
        filter_fields = self.get_filter_fields(req)
        resp.media = [right.to_dict(filter_fields) for right in role.rights]

