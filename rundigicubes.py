"""Testclient"""
import logging
import os

import responder

from starlette.middleware.base import BaseHTTPMiddleware

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from digicubes.common.entities import RoleEntity, RightEntity
from digicubes.server import ressource as endpoint
from digicubes.server.ressource import util
from digicubes.storage import models


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class TestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        print("Greetings from the middelware")
        return response

class DigiCubeServer:
    """
    The DigiCubes Server
    """
    def __init__(self):
        self.port = os.environ.get("DIGICUBE_PORT", 3000)
        secret_key = os.environ.get("DIGICUBE_SECRET", "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o")
        self.db_url = os.environ.get("DIGICUBE_DB_URL", "sqlite://digicubes.db")
        self.api = responder.API(secret_key=secret_key)
        self.api.add_event_handler("startup", self.onStartup)
        self.api.add_event_handler("shutdown", self.onShutdown)
        self.api.add_middleware(TestMiddleware)
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
        return util.createBearerToken(user_id, secret=self.secret_key, minutes=minutes, **kwargs)

    def decodeBearerToken(self, token: str) -> str:
        """Decode a bearer token"""
        return util.decodeBearerToken(token, self.secret_key)

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
