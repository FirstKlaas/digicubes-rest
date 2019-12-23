"""
The endpoint for courses
"""
import logging

from tortoise.exceptions import DoesNotExist
from responder.core import Request, Response

from digicubes_rest.storage.models import School, User, Course
from .util import (
    BasicRessource,
    error_response,
    needs_bearer_token,
    needs_int_parameter,
    has_right,
)


logger = logging.getLogger(__name__)


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
            await School.get(id=school_id)
            data = await req.media()
            data["school_id"] = school_id
            data["created_by_id"] = 1
            resp.status_code, result = await Course.create_ressource(data)
            logger.info("Course successfully created. %d - %s", resp.status_code, result)
            resp.media = result
        except DoesNotExist:
            error_response(resp, 404, "School not found")

        except Exception as error:  # pylint: disable=W0703
            logger.fatal("Something went wrong", exc_info=error)
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
            # Current user.
            user = await User.get(id=self.current_user.id)
            if await has_right(user, ["READ_ALL_COURSES"]):
                # First check, if the current user is assigned to the
                # school referenced by the id.
                # school = (
                #    await School.filter(id=school_id)
                #    .filter(students__id=self.current_user.id)
                #    .first()
                # )
                # if school is None:
                # Current user has not the right to see the courses.
                # error_response(resp, 403, "Insufficient rights to read courses of school.")
                # return

                courses = await Course.filter(school__id=school_id)
                filter_fields = self.get_filter_fields(req)
                resp.media = [course.unstructure(filter_fields) for course in courses]
            else:
                error_response(resp, 403, "Insufficient rights to see the courses.")

        except DoesNotExist:
            error_response(resp, 404, "Ressource not found")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Something went wrong", exc_info=error)
            error_response(resp, 500, str(error))
