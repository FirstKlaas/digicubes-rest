import json
import logging

from digicubes.storage.models import User, Role
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


class RoleRigthsRoute(BasicRessource):
    @needs_int_parameter('id')
    async def on_get(self, req, resp, *, id):
        role = await Role.get(id=id).prefetch_related("rights")
        filter_fields = self.get_filter_fields(req)
        resp.media = [right.to_dict(filter_fields) for right in role.rights]