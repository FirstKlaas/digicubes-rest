import asyncio
from tortoise import Tortoise



def generate_model_documentation():
    """
    Generates a *.rst file for each model registered in Tortoise ORM
    which documents the Fields and Relations.
    """
    #related_model = cls.apps[related_app_name][related_model_name]
    print(Tortoise.apps)


async def run():
    try:
        await Tortoise.init(
            db_url='sqlite://:memory:',
            modules={'model': ['digicubes_rest.storage.models']}
        )
        generate_model_documentation()

    finally:    
        await Tortoise.close_connections()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()

    
