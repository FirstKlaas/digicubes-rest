"""Testclient"""
import logging

import responder
from tortoise import Tortoise

from digicubes.server import ressource as endpoint

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


api.add_route("/users/", endpoint.UsersRessource)
api.add_route("/users/{id}", endpoint.UserRessource)
api.add_route("/users/{id}/roles/", endpoint.UserRolesRessource)
api.add_route("/users/{user_id}/roles/{role_id}", endpoint.UserRoleRessource)

api.add_route("/roles/", endpoint.RolesRessource)
api.add_route("/roles/{id}", endpoint.RoleRessource)
api.add_route("/roles/{id}/rights/", endpoint.RoleRightsRessource)

api.add_route("/rights/", endpoint.RightsRessource)
api.add_route("/rights/{id}", endpoint.RightRessource)
api.add_route("/rights/{id}/roles/", endpoint.RightRolesRessource)
api.add_route("/rights/{right_id}/roles/{role_id}", endpoint.RightRoleRessource)

api.add_route("/schools/", endpoint.SchoolsRessource)
api.add_route("/school/{id}", endpoint.SchoolRessource)

if __name__ == "__main__":    
    api.run()
