"""
Some Test classes the initialize the database
on startup and shut it on tearDown.
"""
import asyncio
from unittest import TestCase as TC

from asynctest import TestCase
import responder
from tortoise import Tortoise

from digicubes.storage.models import User
from digicubes.server import ressource as endpoint


async def init_digicubes_orm():
    """
    Coroutine to initalize the database
    """
    await Tortoise.init(db_url="sqlite://:memory:", modules={"model": ["digicubes.storage.models"]})
    await Tortoise.generate_schemas()


async def close_digicubes_orm():
    """
    Coroutine to shutdown tortoise rom
    """
    await Tortoise.close_connections()


class BasicOrmTest(TestCase):
    """
    Basic ORM Test
    """

    async def setUp(self):
        """
        Init the database in memory
        """
        await init_digicubes_orm()

    async def tearDown(self):
        """
        Shutdown tortoise rom
        """
        await close_digicubes_orm()


class BasicServerTest(TC):
    """
    Basic Server Test
    """

    def setUp(self):
        """
        Init the database in memory
        """
        self.api = responder.API()
        self.api.add_route("/users/", endpoint.UsersRessource)
        self.api.add_route("/users/{user_id}", endpoint.UserRessource)
        self.api.add_route("/users/{user_id}/roles/", endpoint.UserRolesRessource)
        self.api.add_route("/users/{user_id}/roles/{role_id}", endpoint.UserRoleRessource)

        self.api.add_route("/roles/", endpoint.RolesRessource)
        self.api.add_route("/roles/{role_id}", endpoint.RoleRessource)
        self.api.add_route("/roles/{role_id}/rights/", endpoint.RoleRightsRessource)

        self.api.add_route("/rights/", endpoint.RightsRessource)
        self.api.add_route("/rights/{right_id}", endpoint.RightRessource)
        self.api.add_route("/rights/{right_id}/roles/", endpoint.RightRolesRessource)
        self.api.add_route("/rights/{right_id}/roles/{role_id}", endpoint.RightRoleRessource)

        self.api.add_route("/schools/", endpoint.SchoolsRessource)
        self.api.add_route("/school/{school_id}", endpoint.SchoolRessource)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(init_digicubes_orm())

    def tearDown(self):
        """
        Now shut down the database
        """
        self.loop.run_until_complete(close_digicubes_orm())
