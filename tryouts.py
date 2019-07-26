"""
Query Tests
"""
import asyncio
import logging

from tortoise import Tortoise

from digicubes.storage import models

logging.basicConfig(level=logging.INFO)

async def onStartup():
    """
    Initialise the database during startup of the webserver.
    """
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'model': ['digicubes.storage.models']}
    )

async def onShutdown():
    """
    Shutdown the database during startup of the webserver.
    """
    await Tortoise.close_connections()

async def run():
    """ Main run"""
    try:
        await onStartup()
        await Tortoise.generate_schemas()
        user = await models.User.create(login="ratchet")
        role_admin = await models.Role.create(name="admin")
        role_user = await models.Role.create(name="user")
        right_A = await models.Right.create(name="A")
        right_B = await models.Right.create(name="B")

        await role_admin.rights.add(right_A)
        await role_user.rights.add(right_B)
        await role_user.rights.add(right_A)

        await user.roles.add(role_admin)
        await user.roles.add(role_user)

        rights = await models.Right.filter(roles__users__id=1).distinct().values('name')
        print([right["name"] for right in rights])
    finally:
        await onShutdown()

loop = asyncio.get_event_loop()

loop.run_until_complete(run())
