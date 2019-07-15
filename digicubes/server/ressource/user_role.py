# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import User, Role
from .util import BasicRessource, error_response, needs_int_parameter

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UserRoleRessource(BasicRessource):
    """
    Endpoint for a single role that is associated to a single user.

    Supported verbs ``get``, put``, ``delete``
    """

    @needs_int_parameter("role_id")
    @needs_int_parameter("user_id")
    async def on_get(self, req: Request, resp: Response, *, user_id: int, role_id: int):
        """
        Get a role, that is associated to a certain user.

        The requested user is specified by the id. If no user is found a status of 404 is
        send back.

        :param int user_id: The id of the user
        :param int role_id: the id of the role
        """
        try:
            role = await Role.get(id=role_id, users__id=user_id)
            resp.media = role.unstructure()
        except DoesNotExist:
            resp.status_code = 404

    @needs_int_parameter("role_id")
    @needs_int_parameter("user_id")
    async def on_delete(self, req: Request, resp: Response, *, user_id: int, role_id: int):
        """
        Remove a role from the list of associated roles for a user

        :param int user_id: The user id
        :param int role_id: The id of the role
        """
        try:
            user = await User.get(id=user_id).prefetch_related("roles")
            role_id = int(role_id)
            for role in user.roles:
                if role.id is role_id:
                    await user.roles.remove(role)
                    return
            error_response(resp, 404, "Role not found")
            return

        except DoesNotExist:
            error_response(resp, 404, "User not found")
            return

    @needs_int_parameter("role_id")
    @needs_int_parameter("user_id")
    async def on_put(self, req: Request, resp: Response, *, user_id: int, role_id: int):
        """
        Adding a role to a user

        Adds a role to a user. If the specified user or the
        specified user does not exist, a status code of 404
        is returned.

        :param user_id: The id of the user
        :param role_id: The id of the role you want to add to the user
        """
        try:
            user = await User.get(id=user_id)
            role = await Role.get(id=role_id)
            await user.roles.add(role)
        except DoesNotExist:
            error_response(resp, 404, "User not found")
