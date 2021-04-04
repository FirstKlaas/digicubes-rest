"""
The endpoint for rights
"""
import logging

from responder.core import Request, Response

from digicubes_rest.model import RightListModel, RightModel
from digicubes_rest.storage.models import Right

from .util import BasicRessource, BluePrint, error_response, needs_bearer_token

logger = logging.getLogger(__name__)
rights_blueprint = BluePrint()
route = rights_blueprint.route


@route("/rights/")
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
            RightListModel(
                __root__=[RightModel.from_orm(right) for right in await Right.all()]
            ).send_json(resp)

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
        right = await RightModel.create_from_json(data)
        resp.media = right.json()
        resp.status_code = 201

    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response) -> None:
        """
        405 Method not allowed
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
