# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.query_utils import Prefetch

from digicubes_rest.model import SchoolModel
from digicubes_rest.storage.models import User, School

from .util import BasicRessource, BluePrint, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103
me_schools_blueprint = BluePrint()
route = me_schools_blueprint.route


@route("/me/{space}/schools/")
class MeSchoolsRessource(BasicRessource):
    """
    Get all schools of the current user. These are the schools,
    the user is directly associated to. This should be a superset
    of schools where the user is assióciated indirectly to via courses
    """

    # TODO: Method not allowed for the other verbs.

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, space: str) -> None:
        """
        Get a user

        :param int user_id: The id of the user.
        """
        space_relation = {
            "student": "student_schools",
            "headmaster": "principal_schools",
            "teacher": "teacher_schools",
        }
        try:
            user = None
            relation = space_relation.get(space, None)

            if relation is None:
                resp.status_code = 404
                resp.text = "unknown relation type"
            else:
                query = User.get_or_none(id=self.current_user.id).prefetch_related(
                    Prefetch(relation, queryset=self.only(req, School.all()))
                )
                user = await query
                SchoolModel.list_model(
                    [
                        SchoolModel.from_orm(school) for school in getattr(user, relation, [])
                    ]
                ).send_json(resp)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
