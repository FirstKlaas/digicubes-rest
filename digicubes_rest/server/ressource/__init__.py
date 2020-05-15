# pylint: disable=missing-docstring
from typing import List

import logging

from digicubes_rest.storage.models import Right

from .login import login_blueprint
from .renew_token import renew_token_blueprint
from .password import password_blueprint
from .users import users_blueprint
from .user import user_blueprint
from .user_roles import user_roles_blueprint
from .user_role import user_role_blueprint
from .user_rights import user_rights_blueprint

from .roles import roles_blueprint
from .role import role_blueprint
from .role_rights import role_rights_blueprint
from .role_right import role_right_blueprint

from .rights import rights_blueprint
from .right import right_blueprint
from .right_roles import right_roles_blueprint
from .right_role import right_role_blueprint

from .schools import schools_blueprint
from .school import school_blueprint

from .school_courses import school_course_blueprint
from .school_students import school_students_blueprint

from .course import course_blueprint
from .units import units_blueprint

from .me import me_blueprint
from .me_roles import me_roles_blueprint
from .me_rights import me_rights_blueprint
from .me_schools import me_schools_blueprint

from .info import info_blueprint

logger = logging.getLogger(__name__)


def add_routes(api):
    """
    Register all known routes
    """

    # Adding all routes dealing with users
    user_blueprint.register(api)
    users_blueprint.register(api)
    user_role_blueprint.register(api)
    user_roles_blueprint.register(api)
    user_rights_blueprint.register(api)

    # Adding all routs dealing with roles
    role_blueprint.register(api)
    roles_blueprint.register(api)
    role_right_blueprint.register(api)
    role_rights_blueprint.register(api)

    # Adding all routes dealing with rigths
    rights_blueprint.register(api)
    right_blueprint.register(api)
    right_role_blueprint.register(api)
    right_roles_blueprint.register(api)

    # Adding all routes dealing with schools
    school_blueprint.register(api)
    schools_blueprint.register(api)
    school_course_blueprint.register(api)
    school_students_blueprint.register(api)

    # Adding all routes related to courses
    course_blueprint.register(api)

    # Adding all route dealing with units
    units_blueprint.register(api)

    # Adding more service routes
    renew_token_blueprint.register(api)
    login_blueprint.register(api)
    info_blueprint.register(api)
    password_blueprint.register(api)

    # Adding all routes dealing with the current user (me)
    me_blueprint.register(api)
    me_roles_blueprint.register(api)
    me_rights_blueprint.register(api)
    me_schools_blueprint.register(api)


async def get_user_rights(user_id: int) -> List[str]:
    rights = await Right.filter(roles__users__id=1).distinct().values("name")
    return [right["name"] for right in rights]
