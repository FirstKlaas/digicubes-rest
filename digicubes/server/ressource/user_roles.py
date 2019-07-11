import json
import logging
from typing import List, Optional
from digicubes.storage.models import User
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions

from .util import BasicRessource, error_response
import functools

logger = logging.getLogger(__name__)


class UserRolesRoute(BasicRessource):
    async def on_get(self, req, resp, *, id):
        user = await User.get(id=id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in user.roles]
