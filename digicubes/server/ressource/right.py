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

class RightRoute(BasicRessource):
    """
    All service call for a single `right` ressource.
    """
    @needs_int_parameter('id')
    async def on_get(self, req, resp, *, id):
        """
            Requesting a right. The right is identified
            by its id. If no right is found, a 404 response
            status is send back.
        """
        logger.debug(f"GET /rights/{id}/")
        try:
            right = await Right.get(id=id)
            resp.media = right.to_dict(self.get_filter_fields(req))
        except DoesNotExist:
            resp.status = 404

    @needs_int_parameter('id')
    async def on_delete(self, req, resp, *, id):
        """
            Deleting a single right form the database. The right is identified 
            by his id. If no right with the given id exists, a reponse status 404
            is send back.
        """
        logger.debug(f"DELETE /rights/{id}/")
        try:
            right = await Right.get(id=id)
            await right.delete()
            resp.media = right.to_dict()
        except DoesNotExist:
            logger.info(f"Right with id {id} not found in the database.")
            resp.status_code = 404
            resp.media = {"errors": [{"msg": f"Right with id {id} does not exist."}]}
