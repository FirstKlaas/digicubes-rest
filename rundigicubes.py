import asyncio
import responder
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
import logging

logging.basicConfig(level=logging.INFO)

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

api.add_route("/users/", route.UsersRoute)
api.add_route("/users/{id}", route.UserRoute)
api.add_route("/users/{id}/roles/", route.UserRolesRoute)
api.add_route("/users/{user_id}/roles/{role_id}", route.UserRoleRoute)

api.add_route("/roles/", route.RolesRoute)
api.add_route("/roles/{id}", route.RoleRoute)
api.add_route("/roles/{id}/rights/", route.RoleRigthsRoute)

api.add_route("/rights/", route.RightsRoute)
api.add_route("/rights/{id}", route.RightRoute)
api.add_route("/rights/{id}/roles/", route.RightRolesRoute)
api.add_route("/rights/{right_id}/roles/{role_id}", route.RightRoleRoute)

api.add_route("/schools/", route.SchoolsRoute)
api.add_route("/school/{id}", route.SchoolRoute)

if __name__ == "__main__":    
    api.run()
