# pylint: disable=missing-docstring
import logging
import asyncio

from tortoise import Tortoise

from digicubes_rest.storage.models.org import User
from digicubes_client.client.proxy import UserProxy

LOGGER = logging.getLogger(__name__)

async def do_test():
    # pylint: disable=missing-docstring
    LOGGER.info("Initialising orm backend using config.json")
    try:
        await Tortoise.init(
            db_url='sqlite://digicubes.db',
            modules={'model': ['digicubes_rest.storage.models']}
        )
        proxy = UserProxy(login="ratchet", first_name="ratchet")
        user = await User.create(login="ratchet", firstname="clank")
        print(user)
        
    finally:
        await Tortoise.close_connections()

if __name__ == '__main__':
    import sys
    if sys.version_info[0] != 3:
        raise ValueError("Wrong python version. Need >3.5")

    if sys.version_info[1] >= 7:
        asyncio.run(do_test()) # pylint: disable=E1101
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(do_test())
        loop.close()
