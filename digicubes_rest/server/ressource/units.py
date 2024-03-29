"""
RESP API endpoints for the units ressource.

A unit is a part of a course. A course can have multiple
units. Units have a natural order. THe oerder criteria
is the

The endpoints cover the creation of a new unit as well as requesting
all units of an existing course.

METHOD POST
Create an new unit ressource.

METHOD GET
Get all units associated with a course.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import IntegrityError

from digicubes_rest.model import UnitModel
from digicubes_rest.storage import models

from .util import (BasicRessource, BluePrint, error_response,
                   needs_bearer_token, needs_int_parameter)

logger = logging.getLogger(__name__)  # pylint: disable=C0103


units_blueprint = BluePrint()
route = units_blueprint.route


@route("/course/{course_id}/units/")
class UnitsRessource(BasicRessource):
    """
    Units as parts of a course
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

    @needs_bearer_token()
    @needs_int_parameter("course_id")
    async def on_post(self, req: Request, resp: Response, *, course_id: int):
        """
        Create a new unit as part of an course
        """
        try:
            logger.debug("Creating new unit for course %d", course_id)
            # First check, if this is a valid course which exists
            course: models.Course = await models.Course.get_or_none(id=course_id)

            # If not, send a 404 response
            if course is None:
                logger.error("Course not found. Unit cannot be created.")
                resp.status_code = 404
                resp.text = f"Course with id {course_id} not found."

            else:
                # Read the unit definition from the body.
                data = await req.media()
                logger.debug("Provided data %s", data)
                unit_name = data.get("name", None)
                if not unit_name:
                    # No unit name? It is mandatory.
                    resp.status_code = 400
                    resp.text = "No (or empty) unit name provided. Field is mandatory."
                    return

                # Now see, if this course already has a unit with this name,
                # as the name has to be unique within the scope of the
                # course.
                test_unit: models.Unit = await models.Unit.get_or_none(
                    course=course, name=unit_name
                )
                if test_unit is not None:
                    resp.status_code = 409
                    resp.text = (
                        f"Course {course.name} [{course.id}] already "
                        f"has a unit with the name {unit_name}. Must be unique."
                    )
                    return

                logger.debug("Creating new unit")

                unit_model = await UnitModel.orm_create_from_obj(course_id=course_id, data=data)
                unit_model.send_json(resp, status_code=201)

        except IntegrityError:
            logger.exception("Could not create unit")
            resp.status_code = 409  # Conflict
            resp.text = (
                f"Course {course.name} [{course.id}] already has a"
                f"unit with the name {unit_name}. Must be unique."
            )

        except Exception as error:  # pylint: disable=W0703
            logger.exception(
                "Could not create school, based on data %s",
                data,
                exc_info=error,
            )
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    @needs_int_parameter("course_id")
    async def on_get(self, req: Request, resp: Response, *, course_id: int):
        """
        Returns all units for this course
        """
        try:
            # First check, if the course exists
            course = await models.Course.get_or_none(id=course_id)
            if course is None:
                resp.status_code = 404
                resp.text = f"Course with id {course_id} not found."
                return

            units = await models.Unit.filter(course=course).order_by("position")
            # filter_fields = self.get_filter_fields(req)
            UnitModel.list_model([UnitModel.from_orm(unit) for unit in units]).send_json(resp)
        except Exception as error:  # pylint: disable=W0703
            logger.exception("Cannot get units for course %d", course_id)
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response):
        """
        405 Method not allowed
        """
        try:
            resp.text = ""
            resp.status_code = 405  # Method not allowed
            resp.headers["Allow"] = self.ALLOWED_METHODS

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response):
        """
        Deletes all schools
        """
        try:
            resp.status_code = 501  # Not implemented
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
