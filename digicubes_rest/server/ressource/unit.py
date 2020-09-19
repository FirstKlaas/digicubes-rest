"""
API endpoints for a unit.

author: klaas@nebuhr.de
"""

import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.storage import models

from .util import BasicRessource, needs_bearer_token, needs_int_parameter, BluePrint, error_response

logger = logging.getLogger(__name__)  # pylint: disable=C0103


unit_blueprint = BluePrint()
route = unit_blueprint.route


@route("/unit/{unit_id}")
class UnitRessource(BasicRessource):
    """
    Manage an unit
    """

    ALLOWED_METHODS = "GET, PUT, DELETE"

    @needs_bearer_token()
    @needs_int_parameter("unit_id")
    async def on_get(self, req: Request, resp: Response, *, unit_id: int):
        """
        Get an unit identified by its ID
        """
        logger.debug("Requesting unit with id %d", unit_id)
        # First check, if this is a valid course which exists
        db_unit: models.Unit = await models.Unit.get_or_none(id=unit_id)

        # If not, send a 404 response
        if db_unit is None:
            logger.error("UNit not found.")
            resp.status_code = 404
            resp.text = f"Unit with id {unit_id} not found."

        else:
            resp.media = db_unit.unstructure(filter_fields=self.get_filter_fields(req))
            resp.status_code = 200

    @needs_bearer_token()
    @needs_int_parameter("unit_id")
    async def on_delete(self, req: Request, resp: Response, *, unit_id: int):
        """
        Delete an unit identified by its ID
        """
        try:
            db_unit: models.Unit = await models.Unit.get_or_none(id=unit_id)
            if db_unit is None:
                resp.status_code = 404
                resp.text = f"Unit with id {unit_id} does not exist."
            else:
                await db_unit.delete()
                filter_fields = self.get_filter_fields(req)
                resp.media = db_unit.unstructure(filter_fields)

        except DoesNotExist:
            error_response(resp, 404, f"Unit with id {unit_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not delete unit with id %d", unit_id)
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    @needs_int_parameter("unit_id")
    async def on_put(self, req: Request, resp: Response, *, unit_id: int):
        """
        Update an unit identified by its ID
        """
        db_unit: models.Unit = await models.Unit.get_or_none(id=unit_id)
        if db_unit is None:
            resp.status_code = 404
            resp.text = f"Unit with id {unit_id} does not exist."
        else:
            data = await req.media()

            # That's not the most elegant version. The two
            # attributes are write protected, so I pop
            # the two values from the data dict (if present).
            data.pop("created_at", None)
            data.pop("modified_at", None)

            db_unit.update(data)
            await db_unit.save()
            resp.media = db_unit.unstructure(self.get_filter_fields(req))
