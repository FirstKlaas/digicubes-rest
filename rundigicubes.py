import asyncio
import responder
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
import logging

logging.basicConfig(level=logging.DEBUG)

async def onStartup():
    await Tortoise.init(
        db_url='sqlite://digicubes.db',
        modules={'model': ['digicubes.storage.models']}
    )

async def onShutdown():
    await Tortoise.close_connections()

api = responder.API()
api.add_event_handler("startup", onStartup)
api.add_event_handler("shutdown", onShutdown)

@api.route("/")
def index(req, resp):
    resp.text = "DigiCubes"

from digicubes.server import ressource as route

api.add_route("/users/", route.UsersRessource)
api.add_route("/users/{id}", route.UserRessource)
api.add_route("/users/{id}/roles/", route.UserRolesRessource)
api.add_route("/users/{user_id}/roles/{role_id}", route.UserRoleRessource)

api.add_route("/roles/", route.RolesRessource)
api.add_route("/roles/{id}", route.RoleRessource)
api.add_route("/roles/{id}/rights/", route.RoleRigthsRessource)

api.add_route("/rights/", route.RightsRessource)
api.add_route("/rights/{id}", route.RightRessource)
api.add_route("/rights/{id}/roles/", route.RightRolesRessource)
api.add_route("/rights/{right_id}/roles/{role_id}", route.RightRoleRessource)

api.add_route("/schools/", route.SchoolsRessource)
api.add_route("/school/{id}", route.SchoolRessource)

if __name__ == "__main__":    
    api.run()
