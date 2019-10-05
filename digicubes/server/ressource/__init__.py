# pylint: disable=missing-docstring
from typing import List

from digicubes.configuration import Route, url_for
from digicubes.storage.models import Right

from .login import LoginRessource
from .renew_token import RenewTokenRessource
from .password import PasswordRessource
from .users import UsersRessource
from .user import UserRessource
from .user_roles import UserRolesRessource
from .user_role import UserRoleRessource
from .user_rights import UserRightsRessource

from .roles import RolesRessource
from .role import RoleRessource
from .role_rights import RoleRightsRessource
from .role_right import RoleRightRessource

from .rights import RightsRessource
from .right import RightRessource
from .right_roles import RightRolesRessource
from .right_role import RightRoleRessource

from .schools import SchoolsRessource
from .school import SchoolRessource

from .school_courses import SchoolCoursesRessource

from .me import MeRessource
from .me_roles import MeRolesRessource
from .me_rights import MeRightsRessource


def add_routes(api):
    """
    Register all known routes
    """
    api.add_route(Route.me.value, MeRessource)
    api.add_route(Route.me_roles.value, MeRolesRessource)
    api.add_route(Route.me_rights.value, MeRightsRessource)
    api.add_route(Route.login.value, LoginRessource)
    api.add_route(Route.new_token.value, RenewTokenRessource)
    api.add_route(Route.password.value, PasswordRessource)
    api.add_route(Route.users.value, UsersRessource)
    api.add_route(Route.user.value, UserRessource)
    api.add_route(Route.user_roles.value, UserRolesRessource)
    api.add_route(Route.user_role.value, UserRoleRessource)
    api.add_route(Route.user_rights.value, UserRightsRessource)

    api.add_route(Route.roles.value, RolesRessource)
    api.add_route(Route.role.value, RoleRessource)
    api.add_route(Route.role_rights.value, RoleRightsRessource)
    api.add_route(Route.role_right.value, RoleRightRessource)

    api.add_route(Route.rights.value, RightsRessource)
    api.add_route(Route.right.value, RightRessource)
    api.add_route(Route.right_roles.value, RightRolesRessource)
    api.add_route(Route.right_role.value, RightRoleRessource)

    api.add_route(Route.schools.value, SchoolsRessource)
    api.add_route(Route.school.value, SchoolRessource)

    api.add_route(Route.school_courses.value, SchoolCoursesRessource)


async def get_user_rights(user_id: int) -> List[str]:
    rights = await Right.filter(roles__users__id=1).distinct().values("name")
    return [right["name"] for right in rights]
