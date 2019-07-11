import asyncio
import responder
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from digicubes.server.services import (
    UserService, 
    RoleService, 
    RightService,
    SchoolService
)


async def onStartup():
    await Tortoise.init(
        db_url='sqlite://digicubes.db',
        modules={'model': ['digicubes.storage.models']}
    )

async def onShutdown():
    await Tortoise.close_connections()

api = responder.API()
api.add_event_handler("startup", onStartup)
api.add_event_handler("shutdown", onShutdown)

UserService.register(api)
RoleService.register(api)
RightService.register(api)
SchoolService.register(api)

if __name__ == "__main__":    
    api.run()
