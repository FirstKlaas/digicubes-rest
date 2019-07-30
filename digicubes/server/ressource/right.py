"""
The endpoint for a single right.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Right
from .util import BasicRessource, error_response, needs_int_parameter, needs_bearer_token

logger = logging.getLogger(__name__)


class RightRessource(BasicRessource):
    """
    All service call for a single ``right`` ressource.
    """

    ALLOWED_METHODS = "GET, PUT, DELETE"

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, right_id: int):
        """
            Requesting a right. The right is identified
            by its id. If no right is found, a 404 response
            status is send back.
        """
        logger.debug("GET /rights/%s/", right_id)
        try:
            right = await Right.get(id=right_id)
            resp.media = right.unstructure(self.get_filter_fields(req))
            self.set_timestamp(resp, right)
        except DoesNotExist:
            resp.status = 404
        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, error)

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, right_id: int):
        """
            Deleting a single right form the database. The right is identified
            by his id. If no right with the given id exists, a reponse status 404
            is send back.
        """
        logger.debug("DELETE /rights/%s/", right_id)
        try:
            right = await Right.get(id=right_id)
            await right.delete()
            filter_fields = self.get_filter_fields(req)
            resp.media = right.unstructure(filter_fields)
        except DoesNotExist:
            logger.info("Right with id %s not found in the database.", right_id)
            error_response(resp, 404, f"Right with id {right_id} does not exist.")
        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, error)

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, right_id: int):
        """
        Updates the right
        """
        data = await req.media()
        try:
            right = await Right.get(id=right_id)
            right.update(data)
            await right.save()
            filter_fields = self.get_filter_fields(req)
            resp.media = right.unstructure(filter_fields)
            resp.status_code = 200

        except DoesNotExist:
            error_response(resp, 404, f"No right with id {right_id} found.")
        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, error)

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, right_id: int):
        """
        405 Method not allowed
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
