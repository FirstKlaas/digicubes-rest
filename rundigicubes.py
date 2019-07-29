"""Testclient"""
import logging
import os

import responder
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from digicubes.common.entities import RoleEntity, RightEntity
from digicubes.server import ressource as endpoint
from digicubes.server.ressource import util
from digicubes.storage import models

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
        defaults = {
            "verified" : True, 
            "active" : True
        }
        logger.info("Checking database prerequisits")
        # First get or create the root account
        #root = await models.User.get_or_create(defaults, login="root")
        
        try:
            root = await models.User.get(login="root")
        except DoesNotExist:
            root = await models.User.create(login="root")   

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

        # Now test, if the user has the ROOT_RIGHT
        #sufficient_rights = await util.has_right(root, RightEntity.ROOT_RIGHT)
        #if not sufficient_rights:
        #    logger.info("Root has not sufficient rights. Setting root rights.")
        #    role = await models.Role.get_or_create(name=RoleEntity.ROOT)
        #    right = await models.Right.get_or_create(name=RightEntity.ROOT_RIGHT.name)
        #    # Now add right to role and role to root
        #    await root.roles.add(role)
        #    await role.rights.add(right)
        #    logger.info("Done!")
        #else:
        #    logger.info("Root already has sufficient rights. Ok.")

        logger.info("Initialization of the database is done. Root account is setup.")


    async def onShutdown(self):
        """
        Shutdown the database during startup of the webserver.
        """
        await Tortoise.close_connections()

if __name__ == "__main__":
    server = DigiCubeServer()
    server.run()
