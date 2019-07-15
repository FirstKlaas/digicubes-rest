"""
This is the module doc
"""
import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Role, Right
from .util import BasicRessource, needs_int_parameter


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

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
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
                resp.media = [role.unstructure(filter_fields) for role in right.roles]
                return

            resp.status_code = 404
            resp.text = f"No role with id '{role_id}' found for right '{right.name} [{right.id}]'."

        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"No right with id '{right_id}' found."

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
    async def on_put(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """
        Adds another role to this right.

        Sets the response status code to :code:`200` if the role was
        added to the right successfully.

        If :code:`right_id` refers to no existing right, a status code of
        :code:`404` will be send back.

        :param int right_id: The database id of the right
        :param int role_id: The database id of the role
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            if find_role(right, role_id) is None:
                role = await Role.get(id=role_id)
                await right.roles.add(role)
                await right.save()
            resp.media = [role.unstructure(self.get_filter_fields(req)) for role in right.roles]
        except DoesNotExist:
            resp.status_code = 404
            resp.text = "Role or right not found"

    @needs_int_parameter("right_id")
    @needs_int_parameter("role_id")
<<<<<<< HEAD
    async def on_delete(self, req, resp, *, right_id, role_id):
        """
        Removes a specified role from the list of roles associated
        with this right. The role is not deleted from the database.

        :param int right_id: The database id of the right
        :param int role_id: The database id of the role to be removed
=======
    async def on_delete(self, req: Request, resp: Response, *, right_id: int, role_id: int):
        """
        Deleting a specified role.
>>>>>>> b6b2b031cfa0cc3d475550033ea3bcd5c5d5073e
        """
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            if find_role(right, role_id) is not None:
                role = await Role.get(id=role_id)
                await right.roles.remove(role)
                await right.save()
                for role in right.roles:
                    print(role.name)
            resp.media = [role.unstructure(self.get_filter_fields(req)) for role in right.roles]
        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"Role (id={role_id}) or right (id={right_id}) not found"
