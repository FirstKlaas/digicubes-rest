# pylint: disable = C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import School
from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolStudentsRessource(BasicRessource):
    """
    Endpoint for students asscociated with a certain school.

    Supported verbs: ``get``, ``delete``
    """

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

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, school_id: int):
        """
        Get the students of a certain school.
        """
        try:
            school = await School.get(id=school_id).prefetch_related("students")
            filter_fields = self.get_filter_fields(req)
            resp.media = [student.unstructure(filter_fields) for student in school.students]
        except DoesNotExist:
            error_response(resp, 404, "School not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, school_id: int):
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.text = ""
            resp.headers["Allow"] = "GET, DELETE"

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, school_id: int):
        """
        Removes all students from a school. This operation can not be undone. If the
        user can not be found, a 404 status is send back.
        """
        # TODO: What about courses, the user connected to?
        try:
            school = await School.get(id=school_id).prefetch_related("students")
            await school.students.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"School with id {school_id} not found")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
