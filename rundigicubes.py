"""Testclient"""
import logging

import responder
from tortoise import Tortoise

from digicubes.configuration import Route
from digicubes.server import ressource as endpoint

logging.basicConfig(level=logging.INFO)

async def onStartup():
    """
    Initialise the database during startup of the webserver.
    """
    await Tortoise.init(
        db_url='sqlite://digicubes.db',
        modules={'model': ['digicubes.storage.models']}
    )

async def onShutdown():
    """
    Shutdown the database during startup of the webserver.
    """
    await Tortoise.close_connections()

api = responder.API()
api.add_event_handler("startup", onStartup)
api.add_event_handler("shutdown", onShutdown)

@api.route("/")
def index(req, resp):
    """Home"""
    resp.text = "DigiCubes"


api.add_route(Route.users, endpoint.UsersRessource)
api.add_route(Route.user, endpoint.UserRessource)
api.add_route(Route.user_roles, endpoint.UserRolesRessource)
api.add_route(Route.user_role, endpoint.UserRoleRessource)

api.add_route(Route.roles, endpoint.RolesRessource)
api.add_route(Route.role, endpoint.RoleRessource)
api.add_route(Route.role_rights, endpoint.RoleRightsRessource)
api.add_route(Route.role_right, endpoint.RoleRightRessource)

api.add_route(Route.rights, endpoint.RightsRessource)
api.add_route(Route.right, endpoint.RightRessource)
api.add_route(Route.right_roles, endpoint.RightRolesRessource)
api.add_route(Route.right_role, endpoint.RightRoleRessource)

api.add_route(Route.schools, endpoint.SchoolsRessource)
api.add_route(Route.school, endpoint.SchoolRessource)

if __name__ == "__main__":
    api.run()
