"""
Endpoint for rights associsted to a role.
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.model import RightModel
from digicubes_rest.storage.models import Role

from .util import (BasicRessource, BluePrint, error_response,
                   needs_bearer_token, needs_int_parameter)

logger = logging.getLogger(__name__)
role_rights_blueprint = BluePrint()
route = role_rights_blueprint.route


@route("/role/{role_id}/rights/")
class RoleRightsRessource(BasicRessource):
    """
    Endpoint for rights associsted to a role.
    """

    ALLOWED_METHODS = "GET, DELETE"

    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        Get all rights associated to a role
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            # filter_fields = self.get_filter_fields(req)
            RightModel.list_model(
                [RightModel.from_orm(right) for right in role.rights]
            ).send_json(resp)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, role_id: int):
        """
        Removes all rights from a role. This operation can not be undone. If the
        role can not be found, a 404 status is send back.
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            await role.rights.clear()
            return
        except DoesNotExist:
            error_response(resp, 404, f"Role with id {role_id} not found.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.text = ""

    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, role_id: int) -> None:
        """
        405 Method not allowed
        """
        resp.status_code = 405
        resp.headers["Allow"] = self.ALLOWED_METHODS
        resp.text = ""
