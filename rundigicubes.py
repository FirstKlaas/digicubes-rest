"""Testclient"""
import logging
import os

import responder
from tortoise import Tortoise
import jwt

from digicubes.server import ressource as endpoint

logging.basicConfig(level=logging.INFO)

class DigiCubeServer:
    """
    The DigiCubes Server
    """
    def __init__(self):
        self.port = os.environ.get("DIGICUBE_PORT", 3000)
        self.secret = os.environ.get("DIGICUBE_SECRET", "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o")
        self.api = responder.API()
        self.api.add_event_handler("startup", onStartup)
        self.api.add_event_handler("shutdown", onShutdown)

        endpoint.add_routes(self.api)

    def run(self):
        """
        Run the DigiCubeServer
        """
        self.api.run(port=self.port)

    def createBearerToken(self, user_id: int, **kwargs) -> str:
        """Create a bearer token used for authentificated calls."""
        payload = {'user_id': user_id}
        for key, value in kwargs.items():
            payload[key] = value
        token = jwt.encode(payload, self.secret, algorithm='HS256')
        return token

    def decodeBearerToken(self, token: str) -> str:
        """Decode a bearer token"""
        payload = jwt.decode(token, self.secret, algorithms=['HS256'])
        return payload

async def onStartup():
    """
    Initialise the database during startup of the webserver.
    """
    await Tortoise.init(
        db_url='sqlite://digicubes.db',
        modules={'model': ['digicubes.storage.models']}
    )

async def onShutdown():
    """
    Shutdown the database during startup of the webserver.
    """
    await Tortoise.close_connections()

if __name__ == "__main__":
    server = DigiCubeServer()
    token = server.createBearerToken(user_id=12, name="klaas")
    payload = server.decodeBearerToken(token)
    print(type(payload))
    print(payload)
    server.run()
