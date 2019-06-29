# pylint: disable=missing-docstring
import logging
import asyncio

from tortoise import Tortoise

LOGGER = logging.getLogger(__name__)

async def create():
    # pylint: disable=missing-docstring
    LOGGER.info("Initialising orm backend using config.json")
    await Tortoise.init(config_file="config.json")
    LOGGER.info("Creating database schemas.")
    await Tortoise.generate_schemas()
    LOGGER.info("Schema creation completed.")
    await Tortoise.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create())
