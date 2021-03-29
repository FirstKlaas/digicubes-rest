# pylint: disable=C0111
import logging
from datetime import datetime

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.storage import models
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token, BluePrint

logger = logging.getLogger(__name__)  # pylint: disable=C0103

user_schools_blueprint = BluePrint()
route = user_schools_blueprint.route

@route("/user/{user_id}/{space}/schools/")
class UserSchoolsRessource(BasicRessource):
    """
    Get all schools of the current user. These are the schools,
    the user is directly associated to. This should be a superset
    of schools where the user is assióciated indirectly to via courses
    """

    # TODO: Method not allowed for the other verbs.

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, user_id:int, space:str) -> None:
        """
        Get a user

        :param int user_id: The id of the user.
        """
        space_relation = {
            "student" : "student_schools",
            "headmaster" : "principal_schools",
            "teacher" : "teacher_schools"
        }
        try:
            user = None
            relation = space_relation.get(space, None)

            if relation is None:
                resp.status_code = 404
                resp.text = "unknown relation type"
            else:
                user = await models.User.get_or_none(id=user_id).prefetch_related(relation)
                resp.media = [ school.unstructure(filter_fields=self.get_filter_fields(req)) for school in getattr(user, relation, []) ]

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
