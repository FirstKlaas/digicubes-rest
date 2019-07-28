"""
This is the module doc
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Right, Role
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token


logger = logging.getLogger(__name__)  # pylint: disable=C0103


def find_role(right: Right, role_id: int) -> bool:
    """
    Find a role in the list of associated roles for
    the provided right. The role we are looking for
    is specified by its id.
    """
    for role in right.roles:
        if role.id is role_id:
            return role
    return None


class RightRoleRessource(BasicRessource):
    """
    Operations on a specific role for a specific right.
    Supported verbs are: :code:`GET`, :code:`PUT`, :code:`DELETE`

    """

    ALLOWED_METHODS = "GET, DELETE, PUT"

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """
        Returns a role that is associated with a given right.

        :param int right_id: The id of the right
        :param int role_id: The id of the role that has to be assiociated with the right.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            role = find_role(right, role_id)
            if role is not None:
                filter_fields = self.get_filter_fields(req)
                resp.media = role.unstructure(filter_fields)
                return

            resp.status_code = 404
            resp.text = f"No role with id '{role_id}' found for right '{right.name} [{right.id}]'."

        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"No right with id '{right_id}' found."

        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, error)

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """
        Adds another role to this right.

        Sets the response status code to :code:`200` if the role was
        added to the right successfully.

        If :code:`right_id` refers to no existing right, a status code of
        :code:`404` will be send back.

        If the specified role already is associated to th right, a status
        code of ``304 - Not Modified`` is send back. This doesn't fully conform
        to the http standard, as is does not need any header fields an is
        not sending back any header fields. But it says clearly what heppend.
        Because the role is already associated to this right, the right
        hasn't been modified.

        :param int right_id: The database id of the right
        :param int role_id: The database id of the role
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")

            if find_role(right, role_id) is None:
                role = await Role.get(id=role_id)
                await right.roles.add(role)
                resp.status_code = 200  # Role added. Great.
            else:
                resp.status_code = 304  # Role already related. Not modified
        except DoesNotExist as error:
            resp.status_code = 404
            resp.text = str(error)

        except Exception as error:  # pylint: disable=broad-except
            error_response(resp, 500, error)

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """
        Removing a role from a right.

        Tries to remove the role, specified by the ``role_id`` from right, specified by
        the ``right_id``. If the role or the right does not exist, 404 status is send back.

        If the role exists, but is not associated with the right, a status of ``304 - Not Modified``
        is send back. Indicating, that the ressource hasn't been changed.

        If an unknown exception occurs, a status of 500 is send back.
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            role = find_role(right, role_id)
            if role is not None:
                await right.roles.remove(role)
                resp.status_code = 200
            else:
                resp.status_code = 304  # Not Modified

        except DoesNotExist as error:
            error_response(
                resp, 404, f"Role (id={role_id}) or right (id={right_id}) not found", error
            )

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """405 Method not allowed"""
        resp.status_code = 405
        resp.headers["allow"] = self.ALLOWED_METHODS
        resp.text = ""
