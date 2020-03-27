# pylint: disable=missing-docstring
"""Testclient"""
import logging
import logging.config

import os
from pathlib import Path

import responder

from starlette.middleware.base import BaseHTTPMiddleware

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

import yaml

from digicubes_common.entities import RoleEntity, RightEntity
from digicubes_rest.server import ressource as endpoint
from digicubes_rest.server.middleware import SettingsMiddleware
from digicubes_rest.server.ressource import util
from digicubes_rest.storage import models

logger = logging.getLogger(__name__)


class DigiCubeServer:
    """
    The DigiCubes Server
    """

    def __init__(self):
        # Initializing settings
        self.config = Config()
        # TODO: Read the variables from the settings
        self.port = self.config.port
        secret_key = self.config.secret
        self.db_url = self.config.db_url

        # Inner
        self._inner = _Inner(self)

        # No setup responder
        self.api = responder.API(secret_key=secret_key)
        self.api.add_event_handler("startup", self._inner.onStartup)
        self.api.add_event_handler("shutdown", self._inner.onShutdown)
        self.api.add_middleware(SettingsMiddleware, settings=self.config, api=self.api)
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
            db_url=self.server.db_url, modules={"model": ["digicubes_rest.storage.models"]}
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

        self.default_settings = None
        self.custom_settings = None

        # Read the default settings.
        with open("digicubes_rest/server/cfg/default_configuration.yaml", "r") as f:
            self.default_settings = yaml.safe_load(f)

        # Has a custom settings file been specified?
        cfg_file_name = os.getenv("DIGICUBES_CONFIG_FILE", None)
        configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")

        logging_configuration = os.path.join(configpath, "logging.yaml")
        if os.path.isfile(logging_configuration):
            with open(logging_configuration, "r") as f:
                config = yaml.safe_load(f)
                try:
                    logging.config.dictConfig(config)
                except ValueError:
                    logging.basicConfig(level=logging.DEBUG)
                    logger.fatal("Could not configure logging.", exc_info=True)
        else:
            logging.basicConfig(level=logging.DEBUG)

        if cfg_file_name is not None:
            cfg_file = os.path.join(configpath, cfg_file_name)

            # Let's see, if the file is there
            if os.path.isfile(cfg_file):
                logger.info("Adding settings from '%s'", cfg_file)
                with open(cfg_file, "r") as f:
                    self.custom_settings = yaml.safe_load(f)
            else:
                logger.error("Configuration file '%s' specified does not exist.", cfg_file)
        else:
            logger.info("No custom configuration file specified. Usind the defaults")

    def get(self, key, default=None):
        if self.custom_settings is not None:
            val = self.custom_settings.get(key, None)
            if val is not None:
                return val

        return self.default_settings.get(key, default)

    def __getattr__(self, attr):
        return self.get(attr, None)

    def as_dict(self):
        if self.custom_settings is not None:
            return {**self.custom_settings, **self.default_settings}

        return self.default_settings
