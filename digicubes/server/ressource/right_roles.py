"""
Route endpoint for roles that belong to an right.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Right
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RightRolesRessource(BasicRessource):
    """
    Route endpoint for roles, that belog ro a right.
    """

    ALLOWED_METHODS = "GET, DELETE"

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, right_id: int):
        """
        Get all roles, that belong to the specified id. If no right
        with the given id can be found, a 404 status is send back.

        :param int right_id: The id of the right.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            resp.media = [role.unstructure(filter_fields) for role in right.roles]
            return
        except DoesNotExist:
            error_response(resp, 404, f"Right with id {right_id} not found.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, right_id: int):
        """
        Removes all roles from a  right. This operation can not be undone. If the
        right can not be found, a 404 status is send back.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            await right.roles.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"Right with id {right_id} not found.")
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, "Could not remove all roles from right.", error=error)

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, right_id: int):
        """
        405 Method not allowed
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS

    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, right_id: int):
        """
        405 Method not allowed
        """
        resp.text = ""
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
