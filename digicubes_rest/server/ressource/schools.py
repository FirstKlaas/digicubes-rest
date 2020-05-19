# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes_rest.storage.models import School
from .util import BasicRessource, error_response, needs_bearer_token, BluePrint

logger = logging.getLogger(__name__)  # pylint: disable=C0103

schools_blueprint = BluePrint()
route = schools_blueprint.route


@route("/schools/")
class SchoolsRessource(BasicRessource):
    """
    Schools
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response):
        """
        Create a new school or multiple schools
        """
        try:
            logger.debug("POST /schools/")
            data = await req.media()
            # school: School = await School.create_from(data)
            resp.status_code, resp.media = await School.create_ressource(
                data, self.get_filter_fields(req)
            )

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not create school, based on data %s", data, exc_info=error)
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response):
        """
        Returns all schools
        """
        try:
            filter_fields = self.get_filter_fields(req)
            logger.debug("Requesting %s fields.", filter_fields)
            schools = [School.unstructure(school, filter_fields) for school in await School.all()]
            resp.media = schools

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response):
        """
        405 Method not allowed
        """
        try:
            resp.text = ""
            resp.status_code = 405
            resp.headers["Allow"] = self.ALLOWED_METHODS

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response):
        """
        Deletes all schools
        """
        try:
            await School.all().delete()

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))


@route("/schools/filter/{data}/")
async def get_school_by_attr(req: Request, resp: Response, *, data):
    try:
        result = await schools_blueprint.build_query_set(models.School, req, data)
        if result is None:
            resp.media = None
        elif isinstance(result, int):
            resp.media = result
        elif isinstance(result, models.School):
            resp.media = result.unstructure(exclude_fields=["password_hash"])
        else:
            resp.media = [school.unstructure(exclude_fields=["password_hash"]) for school in result]
    except:  # pylint: disable=bare-except
        logger.exception("Unable to perform filter")
