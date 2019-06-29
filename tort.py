# pylint: disable=missing-docstring
import logging
import asyncio
import json

from tortoise import Tortoise

from digicubes.storage.models import User

LOGGER = logging.getLogger(__name__)

def get_configuration(env):
    with open('configuration.json', 'r') as f:
        return json.load(f)["environments"][env]

async def run(conf):
    # pylint: disable=missing-docstring
    #await Tortoise.init(config_file="config.json")
    print(conf)
    await Tortoise.init(conf)
    await User.create(name="Klaas")
    await User.create(name="Marion")
    await User.create(name="Lena")
    await User.create(name="Lennert")
    await Tortoise.close_connections()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conf = get_configuration("production")
    asyncio.run(run(conf["orm"]))
