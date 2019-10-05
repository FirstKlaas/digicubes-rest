"""
The endpoint for courses
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Course, School, User
from .util import BasicRessource, error_response, needs_bearer_token, needs_int_parameter


logger = logging.getLogger(__name__)


class SchoolCoursesRessource(BasicRessource):
    """
    Endpoint for courses of a defined school
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

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

            print("Query: await School.filter(id=school_id).filter(students__id=self.current_user.id)")
            school = await School.filter(id=school_id).filter(students__id=self.current_user.id)
            print('*'*80)
            print(school)
            print('*'*80)

            school = await School.get(id=school_id).prefetch_related("courses")
            filter_fields = self.get_filter_fields(req)
            resp.media = [course.unstructure(filter_fields) for course in school.courses]
        except DoesNotExist:
            error_response(resp, 404, "School not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))


    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, school_id: int):
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.text = ""
            resp.headers["Allow"] = "GET, DELETE"

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
