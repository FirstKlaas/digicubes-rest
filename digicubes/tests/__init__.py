"""
Some Test classes the initialize the database
on startup and shut it on tearDown.
"""
import asyncio
from datetime import timedelta
import logging
from unittest import TestCase
from typing import Optional

# from asynctest import TestCase
from simple_settings import LazySettings
from tortoise import Tortoise
import responder

from digicubes.common.entities import RightEntity, RoleEntity
from digicubes.storage.models import User, Role, Right
from digicubes.server import ressource as endpoint
from digicubes.server.middleware import SettingsMiddleware

from digicubes.server.ressource import util

from digicubes.client import DigiCubeClient
from digicubes.client.proxy import RoleProxy, UserProxy, RightProxy, SchoolProxy

logging.root.setLevel(logging.FATAL)
logger = logging.getLogger(__name__)

ROOT_LOGIN = "root"
ROOT_PASSWORD = "root"


async def init_digicubes_orm():
    """
    Coroutine to initalize the database
    """


async def close_digicubes_orm():
    """
    Coroutine to shutdown tortoise rom
    """
    await Tortoise.close_connections()


async def init_orm(self):
    """
    Initialize the ORM and create a root user.
    """
    logger.info("Initializing ORM backend with in memory database.")
    await Tortoise.init(db_url="sqlite://:memory:", modules={"model": ["digicubes.storage.models"]})
    logger.info("Creating schemas.")
    await Tortoise.generate_schemas()
    roles = {}
    for role in RoleEntity:
        logger.info("Create role '%s'", role.name)
        roles[role.name] = await Role.create(name=role.name)

    for right in RightEntity:
        right_roles = [roles[name] for name in right.role_names]
        logger.info("Create right '%s' with roles %s", right.name, right_roles)
        db_right = await Right.create(name=right.name)
        for db_role in right_roles:
            await db_right.roles.add(db_role)

        logger.info("Right created: %s", db_right)

    logger.info("Creating root user with default passowrd.")
    self.root = User(login=ROOT_PASSWORD, is_active=True, is_verified=True)
    self.root.password = ROOT_PASSWORD
    await self.root.save()

    for role in list(roles.values()):
        await self.root.roles.add(role)

    logger.info("Root has the following rights %s", await util.get_user_rights(self.root))
    # TODO: Set Password for root


class BasicServerTest(TestCase):
    """
    Basic Server Test
    """

    def setUp(self):
        """
        Init the database in memory
        """
        # Now initialise the orm
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(init_orm(self))

        # Init settings
        self.settings = LazySettings("digicubes.server.settings")
        # The Responder async server
        self.api = responder.API()

        # Add settings middleware
        self.api.add_middleware(SettingsMiddleware, settings=self.settings)

        # Add all the known routes
        endpoint.add_routes(self.api)

        # Finally instanciate the client, so
        # we can easily create and modify
        # ressources in the test cases
        self.client: DigiCubeClient = DigiCubeClient.create_from_server(self)

    def tearDown(self):
        """
        Now shut down the database
        """
        self.loop.run_until_complete(close_digicubes_orm())

    @property
    def secret_key(self):  # pylint: disable=C0111
        return self.api.secret_key

    @property
    def User(self):  # pylint: disable=C0111
        return self.client.user_service

    def login(self, login: str, password: str) -> str:
        """Log into server and return the access token."""
        return self.client.login(login, password)

    @property
    def root_token(self):
        """Login as root and returning his token."""
        return self.login(ROOT_LOGIN, ROOT_PASSWORD).bearer_token

    def create_default_headers(self, token: str):
        # pylint: disable=C0111
        auth_key, auth_value = self.create_authorization_header(token)
        return {auth_key: auth_value, "Accept": "application/json", "Cache-Control": "no-cache"}

    def create_authorization_header(self, token):
        """
        Sets the ``Authorization`` header field to
        a valid bearer token.
        """
        # token = util.create_bearer_token
        # (user_id=user_id, lifetime=lifetime, secret=self.secret_key)
        return ("Authorization", f"Bearer {token}")

    @property
    def Role(self):  # pylint: disable=C0111
        return self.client.role_service

    @property
    def Right(self):  # pylint: disable=C0111
        return self.client.right_service

    @property
    def School(self):  # pylint: disable=C0111
        return self.client.school_service

    def create_ratchet(self, token) -> UserProxy:
        """
        Create a demo User with a login 'ratchet'
        """
        user = self.client.user_service.create(token, UserProxy(login="ratchet"))
        self.assertIsNotNone(user.id)
        self.assertEqual(user.login, "ratchet")
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.modified_at)
        return user

    def create_test_role(self, token, name):
        """
        Create a test role.
        """
        role = self.Role.create(token, RoleProxy(name=name))

        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        self.assertEqual(role.name, name)
        self.assertIsNotNone(role.created_at)
        self.assertIsNotNone(role.modified_at)
        return role

    def create_right(self, token, name: str = "TEST_RIGHT"):
        """
        Create a right
        """
        right = self.Right.create(token, RightProxy(name=name))
        self.assertIsNotNone(right)
        self.assertIsNotNone(right.id)
        self.assertEqual(right.name, name)
        self.assertIsNotNone(right.created_at)
        self.assertIsNotNone(right.modified_at)
        return right

    def create_school(self, token, name: str = "TEST_SCHOOL"):
        """
        Create a school. Only the name will be set.
        """
        school = self.School.create(token, SchoolProxy(name=name))
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
