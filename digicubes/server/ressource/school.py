# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes.storage.models import School
from .util import BasicRessource, needs_int_parameter

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolRoute(BasicRessource):
    """
    Endpoint for a school.
    """

    @needs_int_parameter("school_id")
    async def on_get(self, req: Request, resp: Response, *, school_id: int):
        """
        Get a single school

        :param int school_id: Th id of the requested school.
        """
        school = await School.get(id=school_id)
        resp.media = school.to_dict(self.get_filter_fields(req))
