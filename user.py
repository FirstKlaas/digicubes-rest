import asyncio
import responder
from tortoise import Tortoise

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

@api.route("/user/{id}")
async def moin(req, resp, *, id):
    user = await User.filter(id=id).first()
    print(f"Requesting user with id {id}")
    resp.text = f"user, {user}"

if __name__ == "__main__":
    api.run()
