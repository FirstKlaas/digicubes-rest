# pylint: disable=missing-docstring
import logging
import asyncio
import json

from tortoise import Tortoise

from digicubes.storage.models import User, Role

LOGGER = logging.getLogger(__name__)

async def run():
    # pylint: disable=missing-docstring
    try:
        await Tortoise.init(
            db_url='sqlite://digicubes.db',
            modules={'model': ['digicubes.storage.models']}
        )
        await User.bulk_create([
            User(name="Klaas"),
            User(name="Marion"),
            User(name="Lena"),
            User(name="Lennert")
        ])

        await Role.bulk_create([
            Role(name="Admin"),
            User(name="User"),
            User(name="Root")
        ])

        adminRole = await Role.filter(name="Admin").first()
        klaasUser = await User.filter(name="Klaas").first()

        
        print(adminRole)
        print(klaasUser)

    finally:    
        await Tortoise.close_connections()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())

