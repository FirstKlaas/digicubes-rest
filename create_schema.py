# pylint: disable=missing-docstring
import logging
import asyncio

from tortoise import Tortoise

LOGGER = logging.getLogger(__name__)

async def create():
    # pylint: disable=missing-docstring
    LOGGER.info("Initialising orm backend using config.json")
    try:
        await Tortoise.init(
            db_url='sqlite://digicubes.db',
            modules={'model': ['digicubes.storage.models']}
        )
        LOGGER.info("Creating database schemas.")
        await Tortoise.generate_schemas()
        LOGGER.info("Schema creation completed.")
    finally:
        await Tortoise.close_connections()

if __name__ == '__main__':
    import sys
    if sys.version_info[0] != 3:
        raise ValueError("Wrong python version. Need >3.5")

    if sys.version_info[1] >= 7:
        asyncio.run(create()) # pylint: disable=E1101
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create())
        loop.close()
