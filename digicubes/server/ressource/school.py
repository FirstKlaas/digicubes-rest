# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import School
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolRessource(BasicRessource):
    """
    Endpoint for a school.
    """

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, school_id: int) -> None:
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.headers["Allow"] = "GET, PUT, DELETE"
            resp.text = ""

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, school_id: int):
        """
        Get a single school

        :param int school_id: Th id of the requested school.
        """
        try:
            school = await School.get(id=school_id)
            resp.media = school.unstructure(self.get_filter_fields(req))
            self.set_timestamp(resp, school)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, school_id: int) -> None:
        """
        Updates the school
        """
        data = await req.media()
        if not isinstance(data, dict):
            resp.status_code = 400  # Bad_Request
            resp.text = "Bad formatted body content"
            return

        try:
            school = await School.get(id=school_id)
            school.update(data)
            await school.save()
            filter_fields = self.get_filter_fields(req)
            resp.media = school.unstructure(filter_fields)
            resp.status_code = 200

        except DoesNotExist:
            error_response(resp, 404, f"No school with id {school_id} found.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, school_id: int):
        """
        Delete a school specified by its id. If the school does not exisi, a 404
        status code is send back.

        :param int school_id: The id of the school
        """
        try:
            school = await School.get(id=school_id)
            await school.delete()
            filter_fields = self.get_filter_fields(req)
            resp.media = school.unstructure(filter_fields)
        except DoesNotExist:
            error_response(resp, 404, f"School with id {school_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
