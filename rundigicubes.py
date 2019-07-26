"""Testclient"""
import logging

import responder
from tortoise import Tortoise

from digicubes.server import ressource as endpoint

logging.basicConfig(level=logging.INFO)

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

api = responder.API()
api.add_event_handler("startup", onStartup)
api.add_event_handler("shutdown", onShutdown)

endpoint.add_routes(api)

if __name__ == "__main__":
    api.run()
