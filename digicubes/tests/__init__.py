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

from digicubes.client import DigiCubeClient
from digicubes.client.proxy import RoleProxy, UserProxy, RightProxy, SchoolProxy


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
        self.client = DigiCubeClient(None, self.api.requests)

        # Add all the known routes
        endpoint.add_routes(self.api)
        self.loop = asyncio.get_event_loop()

        # Now initialise the orm
        self.loop.run_until_complete(init_digicubes_orm())

    @property
    def User(self):  # pylint: disable=C0111
        return self.client.user_service

    @property
    def Role(self):  # pylint: disable=C0111
        return self.client.role_service

    @property
    def Right(self):  # pylint: disable=C0111
        return self.client.right_service

    @property
    def School(self):  # pylint: disable=C0111
        return self.client.school_service

    def create_ratchet(self) -> UserProxy:
        """
        Create a demo User with a login 'ratchet'
        """
        user = self.client.user_service.create(UserProxy(login="ratchet"))
        self.assertIsNotNone(user.id)
        self.assertEqual(user.login, "ratchet")
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.modified_at)
        return user

    def create_admin_role(self):
        """
        Create an admin role.
        """
        role = self.Role.create(RoleProxy(name="admin"))

        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        self.assertEqual(role.name, "admin")
        self.assertIsNotNone(role.created_at)
        self.assertIsNotNone(role.modified_at)
        return role

    def create_right(self, name: str = "TEST_RIGHT"):
        """
        Create a right
        """
        right = self.Right.create(RightProxy(name=name))
        self.assertIsNotNone(right)
        self.assertIsNotNone(right.id)
        self.assertEqual(right.name, name)
        self.assertIsNotNone(right.created_at)
        self.assertIsNotNone(right.modified_at)
        return right

    def create_school(self, name: str = "TEST_SCHOOL"):
        """
        Create a school. Only the name will be set.
        """
        school = self.School.create(SchoolProxy(name=name))
        self.assertIsInstance(
            school, SchoolProxy, f"Expected SchoolProxy type, byut got {type(school)}"
        )
        self.assertTrue(hasattr(school, "id"))
        self.assertIsNotNone(school)
        self.assertIsNotNone(school.id)
        self.assertEqual(school.name, name)
        self.assertIsNotNone(school.created_at)
        self.assertIsNotNone(school.modified_at)
        return school

    def tearDown(self):
        """
        Now shut down the database
        """
        self.loop.run_until_complete(close_digicubes_orm())
