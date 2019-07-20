from asynctest import TestCase
import responder
from tortoise import Tortoise

async def init_digicubes_orm():
    await Tortoise.init(
        db_url="sqlite://:memory:", modules={"model": ["digicubes.storage.models"]}
    )

    await Tortoise.generate_schemas()

async def close_digicubes_orm():
    """
    Shutdown tortoise rom
    """
    await Tortoise.close_connections()

class BasicOrmTest(TestCase):
    """
    Basic ORM Test
    """

    async def setUp(self):
        """
        Init the database in memory
        """
        await init_digicubes_orm()

    async def tearDown(self):
        """
        Shutdown tortoise rom
        """
        await close_digicubes_orm()


class BasicServerTest(TestCase):
    """
    Basic Server Test
    """

    def __init__(self, *args, **kwargs):
        self.api = responder.API()
        super().__init__(*args, **kwargs)
