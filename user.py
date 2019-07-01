import asyncio
import responder
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from digicubes.storage.models import User

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

@api.route("/{login}")
async def moin(req, resp, *, login):
    try:
        user = await User.get(login=login)
        resp.text = f"user, {user}"        
    except DoesNotExist:
        resp.text = "No such user"    

if __name__ == "__main__":
    api.run()
