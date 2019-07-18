"""
Route endpoint for roles that belong to an right.
"""
from datetime import datetime
import logging

from responder.core import Request, Response
from tortoise import transactions
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import Right
from .util import BasicRessource, needs_int_parameter, error_response, orm_datetime_to_header_string


logger = logging.getLogger(__name__)  # pylint: disable=C0103


class RightRolesRessource(BasicRessource):
    """
    Route endpoint for roles, that belog ro a right.
    """

    @needs_int_parameter("right_id")
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

    @needs_int_parameter("right_id")
    async def on_delete(self, req: Request, resp: Response, *, right_id: int):
        """
        Removes all roles from a  right. This operation can not be undone. If the
        right can not be found, a 404 status is send back.
        """
        transaction = await transactions.start_transaction()
        try:
            right = await Right.get(id=right_id).prefetch_related("roles")
            await right.roles.clear()
            right.modified_at = datetime.now()
            await right.save()
            resp.headers["Last-Modified"] = orm_datetime_to_header_string(right.modified_at)
            transaction.commit()
            return
        except DoesNotExist:
            error_response(resp, 404, f"Right with id {right_id} not found.")
            transaction.rollback()
        except Exception as error:
            error_response(resp, 500, "Could not remove all roles from right.", error=error)
            transaction.rollback()
