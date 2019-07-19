# pylint: disable=missing-docstring
import logging
import asyncio

from tortoise import Tortoise

from digicubes.storage.models import (User, Role, Right, School)

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

        right_delete_user = await Right.create(name="DELETE_USER")
        root = await Role.get(name="Root")
        await root.rights.add(right_delete_user)

        tgg = await School.create(name="TGG")
        ueg = await School.create(name="UEG")

        adminRole = await Role.get_by_name("Admin")
        klaasUser = await User.filter(login="Klaas").first()
        await klaasUser.roles.add(adminRole)

    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    if sys.version_info[0] is not 3:
        raise ValueError("Wrong python version. Need >3.5")

    print(sys.version_info[2])
    logging.basicConfig(level=logging.INFO)
    if sys.version_info[1] >= 7:
        asyncio.run(run())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        loop.close()
