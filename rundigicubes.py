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
from digicubes.server.ressource import util
from digicubes.storage import models


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class TestMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, digicube=None):
        super().__init__(app)
        self.digicube = digicube

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response

class SettingsMiddleware(BaseHTTPMiddleware):
    """Middleware to inject settings into the request state"""
    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        logger.info("Added settings middleware.")

    async def dispatch(self, request, call_next):
        request.state.settings = self.settings
        print("Middleware settings added to request")
        response = await call_next(request)
        return response

class DigiCubeServer:
    """
    The DigiCubes Server
    """
    def __init__(self):
        # Initializing settings
        settings_sources = ['digicubes.server.settings']
        environ = os.environ.get('DIGICUBES_ENVIRONMENT', 'development')
        environ = f"{environ}.yaml"
        configpath = os.environ.get('DIGICUBES_CONFIG_PATH', 'cfg')
        cfg_file = os.path.join(configpath, environ)

        # Let's see, if the file is there
        if os.path.isfile(cfg_file):
            logger.info("Adding settings from '%s'", cfg_file)
            settings_sources.append(cfg_file)
        else:
            logger.error(
                "Environ '%s' specified by environment variable, but file '%s' does not exist.",
                environ,
                cfg_file)

        settings_sources.append('DIGICUBES_.environ')
        self.settings = LazySettings(*settings_sources)

        self.port = os.environ.get("DIGICUBE_PORT", 3000)
        secret_key = os.environ.get("DIGICUBE_SECRET", "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o")
        self.db_url = os.environ.get("DIGICUBE_DB_URL", "sqlite://digicubes.db")
        self.api = responder.API(secret_key=secret_key)
        self.api.add_event_handler("startup", self.onStartup)
        self.api.add_event_handler("shutdown", self.onShutdown)
        self.api.add_middleware(TestMiddleware, digicube=self)
        self.api.add_middleware(SettingsMiddleware, settings=self.settings)
        self.api.digicube = self
        endpoint.add_routes(self.api)


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
        self.api.run(port=self.port)

    def createBearerToken(self, user_id: int, minutes=30, **kwargs) -> str:
        """Create a bearer token used for authentificated calls."""
        return util.create_bearer_token(user_id, secret=self.secret_key, minutes=minutes, **kwargs)

    def decodeBearerToken(self, token: str) -> str:
        """Decode a bearer token"""
        return util.decode_bearer_token(token, self.secret_key)

    async def onStartup(self):
        """
        Initialise the database during startup of the webserver.
        """
        await Tortoise.init(
            db_url=self.db_url,
            modules={'model': ['digicubes.storage.models']}
        )
        await Tortoise.generate_schemas()
        await self.init_database()

    async def init_database(self):
        """
        Initialize the database with a root user
        to be used as master account.
        """
        # First get or create the root account
        #root = await models.User.get_or_create(defaults, login="root")

        try:
            root = await models.User.get(login="root")
            root.is_active = True
            root.is_verified = True
            if root.password_hash is None:
                root.password_hash = models.hash_password("digicubes")
            await root.save()
            logger.info("Root account exists. Checking fields.")

        except DoesNotExist:
            logger.info("Root does not exist. Creating new account")
            root = await models.User.create(
                login="root",
                password_hash=models.hash_password("digicubes"),
                is_active=True,
                is_verified=True)

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

if __name__ == "__main__":
    server = DigiCubeServer()
    server.run()
