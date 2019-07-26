# pylint: disable=missing-docstring
from digicubes.configuration import Route,url_for

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

def add_routes(api):
    """
    Register all known routes
    """
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
