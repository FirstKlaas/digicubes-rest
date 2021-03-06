# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes_rest.storage.models import User

from .util import BasicRessource, error_response, needs_bearer_token, BluePrint

logger = logging.getLogger(__name__)  # pylint: disable=C0103
me_schools_blueprint = BluePrint()
route = me_schools_blueprint.route


@route("/me/schools/")
class MeSchoolsRessource(BasicRessource):
    """
    Get all schools of the current user. These are the schools,
    the user is directly associated to. This should be a superset
    of schools where the user is assióciated indirectly to via courses
    """

    # TODO: Method not allowed for the other verbs.

    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response) -> None:
        """
        Get a user

        :param int user_id: The id of the user.
        """
        try:
            user = await User.get(id=self.current_user.id)
            user_dict = user.unstructure(
                filter_fields=self.get_filter_fields(req), exclude_fields=["password_hash"]
            )
            resp.media = user_dict
            self.set_timestamp(resp, user)
        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
