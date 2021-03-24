import logging
import os

from tortoise import Tortoise

logger = logging.getLogger(__name__)


async def init_orm():
    database_url = os.getenv("DIGICUBES_DATABASE_URL", "sqlite://:memory:")
    logger.info("Connecting to database %s", database_url)
    await Tortoise.init(db_url=database_url, modules={"model": ["digicubes_rest.storage.models"]})


async def create_schema():
    logger.info("Creating database schemas.")
    await Tortoise.generate_schemas()
    logger.info("Schema creation completed.")


async def shutdown_orm():
    await Tortoise.close_connections()
