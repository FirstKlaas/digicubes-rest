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
            User(login="Klaas"),
            User(login="Marion"),
            User(login="Lena"),
            User(login="Lennert")
        ])

        await Role.bulk_create([
            Role(name="Admin"),
            Role(name="User"),
            Role(name="Root")
        ])

        adminRole = await Role.get_by_name("Admin")
        klaasUser = await User.filter(login="Klaas").first()
        await klaasUser.roles.add(adminRole)
        
        print(adminRole)
        print(klaasUser)

    finally:    
        await Tortoise.close_connections()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())

