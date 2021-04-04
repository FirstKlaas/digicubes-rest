# pylint: disable=C0111
import logging

from responder.core import Request, Response

from digicubes_rest.storage import models

from .util import (BasicRessource, BluePrint, needs_bearer_token,
                   needs_int_parameter)

logger = logging.getLogger(__name__)  # pylint: disable=C0103

school_teacher_blueprint = BluePrint()
route = school_teacher_blueprint.route


@route("/school/{school_id}/teacher/{user_id}/")
class SchoolsTeacherRessource(BasicRessource):
    @needs_int_parameter("school_id")
    @needs_int_parameter("user_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, school_id: int, user_id: int):
        school = await models.School.get_or_none(id=school_id)
        if school is None:
            resp.status_code = 404
            resp.text = "No school found"
            return

        user = await models.User.get_or_none(id=user_id, roles__name="teacher")
        if user is None:
            resp.status_code = 404
            resp.text = "No user found. Maybe id was wrong or the account is not a teacher."
            return

        await school.teacher.add(user)
        resp.status_code = 200
