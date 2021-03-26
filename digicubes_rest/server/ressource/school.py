# pylint: disable=C0111
import logging
from datetime import datetime

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.storage import models
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token, BluePrint

logger = logging.getLogger(__name__)  # pylint: disable=C0103

school_blueprint = BluePrint()
route = school_blueprint.route


@route("/school/{school_id}")
class SchoolRessource(BasicRessource):
    """
    Endpoint for a school.
    """

    @needs_int_parameter("school_id")
    @needs_bearer_token()
    async def on_post(
        self, req: Request, resp: Response, *, school_id: int
    ) -> None:  # pylint: disable=unused-argument
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
            school = await models.School.get(id=school_id)
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

        # That's not the most elegant version. The two
        # attributes are write protected, so I pop
        # the two values from the data dict (if present).
        data.pop("created_at", None)
        data.pop("modified_at", None)

        if not isinstance(data, dict):
            resp.status_code = 400  # Bad_Request
            resp.text = "Bad formatted body content"
            return

        try:
            school: models.School = await models.School.get(id=school_id)
            school.update(data)
            school.modified_at = datetime.utcnow()
            await school.save()
            filter_fields = self.get_filter_fields(req)
            resp.media = school.unstructure(filter_fields)
            resp.status_code = 200

        except DoesNotExist:
            error_response(resp, 404, f"No school with id {school_id} found.")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not update school")
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
            school: models.School = await models.School.get_or_none(id=school_id)
            if school is None:
                resp.status_code = 404
                resp.text = f"School with id {school_id} does not exist."
            else:
                await school.delete()
                filter_fields = self.get_filter_fields(req)
                resp.media = school.unstructure(filter_fields)

        except DoesNotExist:
            error_response(resp, 404, f"School with id {school_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not delete school with id %d", school_id)
            error_response(resp, 500, str(error))


@route("/school/byname/{school_name}")
async def get_school_by_name(req: Request, resp: Response, *, school_name):
    # pylint: disable=unused-variable
    if req.method == "get":
        school = await models.School.get_or_none(name=school_name)
        if school is None:
            resp.status_code = 404
            resp.text = f"School with name {school_name} not found."
        else:
            resp.media = school.unstructure()
    else:
        resp.status_code = 405
        resp.text = "Method not allowed"


@route("/school/{school_id}/teacher/")
async def get_school_teacher(req: Request, resp: Response, *, school_id):

    if req.method == "get":
        school = await models.School.get_or_none(id=school_id).prefetch_related("teacher")
        if school is None:
            resp.status_code = 404
            resp.text = f"School with id {school_id} not found."
        else:
            resp.media = [t.unstructure(exclude_fields=["password_hash"]) for t in school.teacher]
    else:
        resp.status_code = 405
        resp.text = "Method not allowed"
