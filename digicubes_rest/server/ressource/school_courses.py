"""
The endpoint for courses
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.model import CourseModel
from digicubes_rest.storage import models

from .util import (BasicRessource, BluePrint, error_response,
                   needs_bearer_token, needs_int_parameter)

logger = logging.getLogger(__name__)
school_course_blueprint = BluePrint()
route = school_course_blueprint.route


@route("/school/{school_id}/courses/")
class SchoolCoursesRessource(BasicRessource):
    """
    Endpoint for courses of a defined school
    """

    ALLOWED_METHODS = "POST, GET"

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, school_id: int):
        """
        Create a new course for the specified school.

        This is a first unsecure version.
        """
        # TODO: Check the rights! Needs right: CREATE_COURSE and must be
        # associated with the school
        try:
            logger.debug("Trying to create course for school with id %d", school_id)
            await models.School.get(id=school_id)
            data = await req.media()
            course_model = await CourseModel.orm_create_from_obj(school_id=school_id, data=data)

            logger.info(
                "Course successfully created. %d - %s",
                resp.status_code,
                course_model,
            )
            course_model.send_json(resp, status_code=201)

        except DoesNotExist:
            error_response(resp, 404, "School not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, school_id: int):
        """
        Get a list of all courses associated with the
        specified school.
        The school is specified by its id. If an invalid id
        is specified, an 404 status is resturned.

        The specified school has to be associated with the
        curent user (or the current user needs root rights).

        If the school is not associated with the current user
        and the user has no root rights, than a 403 status
        (access forbidden) is returned.

        If everything is ok, than a json array with all
        schools is returned. The x-filter-list header parameter
        is supported.
        """
        try:
            courses = await models.Course.filter(school_id=school_id)
            # filter_fields = self.get_filter_fields(req)
            CourseModel.list_model(
                [CourseModel.from_orm(course) for course in courses]
            ).send_json(resp)

        except DoesNotExist:
            error_response(resp, 404, "Ressource not found")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Something went wrong", exc_info=error)
            error_response(resp, 500, str(error))
