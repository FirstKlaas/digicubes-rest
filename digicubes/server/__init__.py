# pylint: disable=missing-docstring
"""Testclient"""
import logging
import os

import responder

from starlette.middleware.base import BaseHTTPMiddleware

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from simple_settings import LazySettings

from digicubes.common.entities import RoleEntity, RightEntity
from digicubes.server import ressource as endpoint
from digicubes.server.middleware import SettingsMiddleware
from digicubes.server.ressource import util
from digicubes.storage import models


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class DigiCubeServer:
    """
    The DigiCubes Server
    """

    def __init__(self):
        # Initializing settings
        self.config = Config()

        # TODO: Read the variables from the settings
        self.port = os.environ.get("DIGICUBES_PORT", 3000)
        secret_key = os.environ.get("DIGICUBES_SECRET", "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o")
        self.db_url = os.environ.get("DIGICUBES_DB_URL", "sqlite://digicubes.db")

        # Inner
        self._inner = _Inner(self)

        # No setup responder
        self.api = responder.API(secret_key=secret_key)
        self.api.add_event_handler("startup", self._inner.onStartup)
        self.api.add_event_handler("shutdown", self._inner.onShutdown)
        self.api.add_middleware(SettingsMiddleware, settings=self.config)
        self.api.digicube = self
        endpoint.add_routes(self.api)
        self._extensions = []

    def add_extension(self, extension):
        logger.info("Register extension %r", type(extension))
        self._extensions.append(extension)

    @property
    def secret_key(self):
        """
        Returns the secret key.

        The key is used as secret for jwt decoding and encoding. It is also the secret
        key of the responder.API()
        """
        return self.api.secret_key

    def run(self):
        """
        Run the DigiCubeServer
        """
        # First init all extensions
        for extension in self._extensions:
            logger.info("Initialise extension %r.", type(extension))
            extension.init(self)

        # Now start the server
        logger.info("Starting digicubes server on port %d.", self.port)
        self.api.run(port=self.port)

    def createBearerToken(self, user_id: int, minutes=30, **kwargs) -> str:
        """Create a bearer token used for authentificated calls."""
        return util.create_bearer_token(user_id, secret=self.secret_key, minutes=minutes, **kwargs)

    def decodeBearerToken(self, token: str) -> str:
        """Decode a bearer token"""
        return util.decode_bearer_token(token, self.secret_key)

    def mount(self, route, app):
        """Mounts an WSGI / ASGI application at a given route.

        :param route: String representation of the route to be used (shouldn't be parameterized).
        :param app: The other WSGI / ASGI app.
        """
        self.api.mount(route, app)


class _Inner:
    def __init__(self, server):
        self.server = server

    async def onStartup(self):
        """
        Initialise the database during startup of the webserver.
        """
        await Tortoise.init(
            db_url=self.server.db_url, modules={"model": ["digicubes.storage.models"]}
        )
        await Tortoise.generate_schemas()
        await self.init_database()

    async def init_database(self):
        """
        Initialize the database with a root user
        to be used as master account.
        """
        # First get or create the root account
        # root = await models.User.get_or_create(defaults, login="root")

        try:
            root = await models.User.get(login="root")
            root.is_active = True
            root.is_verified = True
            if root.password_hash is None:
                root.password = "digicubes"
            await root.save()
            logger.info("Root account exists. Checking fields.")

        except DoesNotExist:
            logger.info("Root does not exist. Creating new account")
            root = models.User(login="root", is_active=True, is_verified=True)
            root.password = "digicubes"
            await root.save()

        try:
            role = await models.Role.get(name=RoleEntity.ROOT.name)
        except DoesNotExist:
            role = await models.Role.create(name=RoleEntity.ROOT.name)

        await root.roles.add(role)

        try:
            right = await models.Right.get(name=RightEntity.ROOT_RIGHT.name)
        except DoesNotExist:
            right = await models.Right.create(name=RightEntity.ROOT_RIGHT.name)

        await role.rights.add(right)
        logger.info("Initialization of the database is done. Root account is setup.")

    async def onShutdown(self):
        """
        Shutdown the database during startup of the webserver.
        """
        await Tortoise.close_connections()


class Config:
    def __init__(self):
        settings_sources = ["digicubes.server.settings"]
        environ = os.environ.get("DIGICUBES_ENVIRONMENT", "development")
        environ = f"{environ}.yaml"
        configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")
        cfg_file = os.path.join(configpath, environ)

        # Let's see, if the file is there
        if os.path.isfile(cfg_file):
            logger.info("Adding settings from '%s'", cfg_file)
            settings_sources.append(cfg_file)
        else:
            logger.error(
                "Environ '%s' specified by environment variable, but file '%s' does not exist.",
                environ,
                cfg_file,
            )

        settings_sources.append("DIGICUBES_.environ")
        settings_sources.append("DIGICUBE_.environ")
        self._settings = LazySettings(*settings_sources)

    def get(self, key, default=None):
        try:
            return self.__getattr__(key)
        except AttributeError:
            return default

    def __getattr__(self, attr):
        return self._settings.__getattr__(attr)

    def as_dict(self):
        return self._settings.as_dict()
