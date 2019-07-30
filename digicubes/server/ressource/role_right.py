"""
This is the module doc
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Role
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


def _find_right(role: Role, right_id: int) -> bool:
    """
    Find a right in the list of associated rights for
    the provided role. The right we are looking for
    is specified by its id.
    """
    for right in role.rights:
        if right.id is right_id:
            return right
    return None


class RoleRightRessource(BasicRessource):
    """
    Operations on a specific right for a specific role.
    Supported verbs are: :code:`GET`, :code:`PUT`, :code:`DELETE`

    """

    ALLOWED_METHODS = "GET, DELETE, PUT"

    @needs_int_parameter("role_id")
    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, role_id: int, right_id: int):
        """
        Returns a rignt that is associated with a given role.

        :param int role_id: The id of the role that has to be assiociated with the right.
        :param int right_id: The id of the right
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            right = _find_right(role, right_id)
            if right is not None:
                filter_fields = self.get_filter_fields(req)
                resp.media = right.unstructure(filter_fields)
                return

            resp.status_code = 404
            resp.text = f"No role with id '{role_id}' found for right '{right.name} [{right.id}]'."

        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"No right with id '{right_id}' found."

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("role_id")
    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, role_id: int, right_id: int):
        """
        Adds a right to this role.

        Sets the response status code to :code:`200` if the right was
        added to the role successfully.

        If :code:`role_id` refers to no existing role, a status code of
        :code:`404` will be send back.

        If the specified right already is associated to th role, a status
        code of ``304 - Not Modified`` is send back. This doesn't fully conform
        to the http standard, as is does not need any header fields an is
        not sending back any header fields. But it says clearly what happend.
        Because the right is already associated to this role, the role
        hasn't been modified.

        :param int right_id: The database id of the right
        :param int role_id: The database id of the role
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            right = _find_right(role, right_id)
            if right is None:
                await role.right.add(right)
                resp.status_code = 200
            else:
                resp.status_code = 304

        except DoesNotExist as error:
            resp.status_code = 404
            resp.text = str(error)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("role_id")
    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, role_id: int, right_id: int):
        """
        Removing a right from a role.
        """
        try:
            role = await Role.get(id=role_id).prefetch_related("rights")
            right = _find_right(role, right_id)
            if right is not None:
                await role.rights.remove(right)
                resp.status_code = 200
            else:
                resp.status_code = 304  # Not Modified

        except DoesNotExist as error:
            error_response(
                resp, 404, f"Role (id={role_id}) or right (id={right_id}) not found", error
            )

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("role_id")
    @needs_int_parameter("right_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, role_id: int, right_id: int):
        """405 Method not allowed"""
        resp.status_code = 405
        resp.headers["allow"] = self.ALLOWED_METHODS
        resp.text = ""
