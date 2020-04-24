# pylint: disable=missing-docstring
"""Testclient"""
from datetime import timedelta, datetime
import logging
import logging.config

from importlib.resources import open_text
import os
from pathlib import Path

import jwt
import responder

from starlette.middleware.base import BaseHTTPMiddleware

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

import yaml

from digicubes_common.entities import RoleEntity, RightEntity
from digicubes_common.exceptions import DigiCubeError
from digicubes_rest.storage import models
from digicubes_rest.server import ressource as endpoint
from digicubes_rest.server.middleware import SettingsMiddleware, UpdateTokenMiddleware
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
        self.api.digicube = self

        self.api.add_event_handler("startup", self._inner.onStartup)
        self.api.add_event_handler("shutdown", self._inner.onShutdown)
        self.api.add_middleware(SettingsMiddleware, settings=self.config, api=self.api)
        self.api.add_middleware(UpdateTokenMiddleware, settings=self.config, api=self.api)

        endpoint.add_routes(self.api)

        @self.api.route("/verify/user/{data}")
        async def verify_user(req: responder.Request, resp: responder.Response, *, data):

            if req.method == "get":
                """
                Generate a verification token for this user.
                """
                # TODO: Check if the user exists and the account is not
                # verified.
                lifetime = timedelta(hours=6)  # TODO: make this configurable

                payload = {}
                payload["user_id"] = int(data)
                payload["exp"] = datetime.utcnow() + lifetime
                payload["iat"] = datetime.utcnow()
                token = jwt.encode(payload, self.secret_key, algorithm="HS256")
                resp.media = {"token": token.decode("UTF-8"), "user_id": int(data)}
                return

            if req.method == "put":
                token = str(data)
                payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                user_id = payload["user_id"]
                user = await models.User.get(id=user_id)
                user.is_verified = True
                await user.save()
                resp.media = user.unstructure(exclude_fields=["password_hash"])
                return

            resp.status_code = 405
            resp.text = f"Method {req.method} not allowed."

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
        self.api.run(port=self.port, address="0.0.0.0")

    def createBearerToken(self, user_id: int, minutes=180, **kwargs) -> str:
        """Create a bearer token used for authentificated calls."""
        logger.info("Requesting ne bearer token with a lifetime of %d seconds", minutes)
        return util.create_bearer_token(
            user_id, secret=self.secret_key, lifetime=timedelta(minutes=minutes), **kwargs
        )

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
        modules = {
            "model": self.server.config.model,
        }

        # custom_models = self.server.config.custom_models
        # if custom_models is not None:
        #    modules["models"].extend(custom_models)
        await Tortoise.init(db_url=self.server.db_url, modules=modules)
        await Tortoise.generate_schemas()
        await self.init_database()

    async def init_database(self):
        """
        Initialize the database with a root user
        to be used as master account.
        """
        # First get or create the root account
        # root = await models.User.get_or_create(defaults, login="root")

        master_data = self.config.master_data

        # Now we create the initial set of data, we need
        # to run the system.
        for right in master_data["rights"]:
            _, created = await models.Right.get_or_create({}, name=right)
            if created:
                logger.info("Right %s created.", right)
            else:
                logger.debug("Right %s already exists. Good!", right)

        # Now setting up the basic roles
        for role in master_data["roles"]:
            role_name = role["name"]
            db_role, created = await models.Role.get_or_create(
                {
                    "description": role.get("description", ""),
                    "home_route": role.get("home_route", "account.logout"),
                },
                name=role_name,
            )

            if created:
                logger.info("Role %s created. Adding initial rights.", role_name)
                right_names = role["rights"]
                for name in right_names:
                    r, right_created = await models.Right.get_or_create({}, name=name)
                    if right_created:
                        logger.warning(
                            "Right %s created while setting up the role %s. Better define all rights beforehand.",
                            name,
                            role_name,
                        )
                    await db_role.rights.add(r)
                await db_role.save()
            else:
                logger.info("Role %s already exists. Rights will not be changed.", role_name)

        # First make sure, we have a root account.
        try:
            root = await models.User.get(login="root")
            root.is_active = True
            root.is_verified = True
            root.first_name = "DiGi"
            root.last_name = "Cube"
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

    @property
    def config(self):
        return self.server.config


class Config:
    def __init__(self):

        self.default_settings = None
        self.custom_settings = {}

        # Read the default settings.

        # with open("digicubes_rest/server/cfg/default_configuration.yaml", "r") as f:
        #    self.default_settings = yaml.safe_load(f)
        with open_text("digicubes_rest.server.cfg", "default_configuration.yaml") as f:
            self.default_settings = yaml.safe_load(f)

        # Has a custom settings file been specified?
        cfg_file_name = os.getenv("DIGICUBES_CONFIG_FILE", None)
        configpath = os.getenv("DIGICUBES_CONFIG_PATH", "cfg")

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
            logger.info("No custom configuration file specified. Using the defaults")

        # Now checking for certain environment variables, as they overule the settings
        secret = os.getenv("DIGICUBES_SECRET", None)
        if secret is None:
            logger.info(
                (
                    "For scurity reasons, it is highly emphasized to set the secret",
                    " via the environment variable DIGICUBES_SECRET.",
                )
            )
        else:

            self.custom_settings["secret"] = secret

    def get(self, key, default=None):
        """
        Access settings in dict mode.
        """
        if self.custom_settings is not None:
            val = self.custom_settings.get(key, None)
            if val is not None:
                return val

        return self.default_settings.get(key, default)

    def __getattr__(self, attr):
        """
        Accessing settings as attributes
        """
        return self.get(attr, None)

    def as_dict(self):
        """
        Returning merged settings as a dict. The custom settings
        of course have a higher precedence. Corresponding default
        settings are eliminated in the returned dict.
        """
        if self.custom_settings is not None:
            return {**self.custom_settings, **self.default_settings}

        return self.default_settings
