"""
Route endpoint for roles that belong to an right.
"""
import logging

from responder.core import Request, Response

from digicubes.storage.models import Right

from .util import BasicRessource, needs_int_parameter


logger = logging.getLogger(__name__)  # pylint: disable=C0103


<<<<<<< HEAD
class RightRolesRessource(BasicRessource):
    """
    Operation on the roles of a given right.

    Supported verbs are: :code:`GET`, :code:`DELETE`
    """

    @needs_int_parameter("id")
    async def on_get(self, req, resp, *, id):
        """
        Get all routes associated with this right.
        """
        right = await Right.get(id=id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.to_dict(filter_fields) for role in right.roles]

    @needs_int_parameter("id")
    async def on_delete(self, req, resp, *, id):
        """
        Removes all roles from the list of asscociated roles from the right.
        """
        try:
            right = await Right.get(id=id).prefetch_related("roles")
            filter_fields = self.get_filter_fields(req)
            await right.roles.clear()
            resp.media = [role.to_dict(filter_fields) for role in right.roles]
        except DoesNotExist:
            resp.status_code = 404
            resp.text = f"Right with id {id} does not exist."
=======
class RightRolesRoute(BasicRessource):
    """
    Route endpoint for roles, that belog ro a right.
    """

    @needs_int_parameter("right_id")
    async def on_get(self, req: Request, resp: Response, *, right_id: int):
        """
        Get all roles, that belong to the speciefied id.

        :param int right_id: The id of the right.
        """
        right = await Right.get(id=right_id).prefetch_related("roles")
        filter_fields = self.get_filter_fields(req)
        resp.media = [role.unstructure(filter_fields) for role in right.roles]
>>>>>>> b6b2b031cfa0cc3d475550033ea3bcd5c5d5073e
