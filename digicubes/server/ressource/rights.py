"""
The endpoint for rights
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right
from .util import BasicRessource, error_response, needs_bearer_token


logger = logging.getLogger(__name__)


class RightsRessource(BasicRessource):
    """
    Endpoint for rights
    """

    ALLOWED_METHODS = "POST, GET, DELETE"

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response):
        """
        Get a list of all rights
        """
        try:
            filter_fields = self.get_filter_fields(req)
            logger.debug("Requesting %s fields.", filter_fields)
            rights = [right.unstructure(filter_fields) for right in await Right.all()]
            resp.media = rights

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response):
        """
        Deletes all rights.
        """
        await Right.all().delete()

    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response) -> None:
        """
        Create new right ressource.
        """
        data = await req.media()
        resp.status_code, resp.media = await Right.create_ressource(data)

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response) -> None:
        """
        405 Method not allowed
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
