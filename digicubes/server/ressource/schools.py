# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import School
from .util import BasicRessource, create_ressource, error_response

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolsRessource(BasicRessource):
    """
    Schools
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

    async def on_post(self, req: Request, resp: Response):
        """
        Create a new school or multiple schools
        """
        try:
            logger.debug("POST /schools/")
            data = await req.media()
            resp.status_code, resp.media = await create_ressource(School, data)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    async def on_get(self, req: Request, resp: Response):
        """
        Returns all schools
        """
        try:
            filter_fields = self.get_filter_fields(req)
            logger.debug("Requesting %s fields.", filter_fields)
            schools = [school.unstructure(filter_fields) for school in await School.all()]
            resp.media = schools

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

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

    async def on_delete(self, req: Request, resp: Response):
        """
        Deletes all schools
        """
        try:
            await School.all().delete()

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
