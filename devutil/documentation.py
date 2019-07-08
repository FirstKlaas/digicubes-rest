import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import asyncio
from tortoise import Tortoise
from tortoise.models import fields



def generate_model_documentation():
    """
    Generates a *.rst file for each model registered in Tortoise ORM
    which documents the Fields and Relations.
    """

    def write_model_rst(app, name, model):
        meta = model._meta
        with open(f"tmp/{app_name}_{name}.rst", "w") as f:
            f.write(f"{name}\n")
            f.write("-" * len(name))
            f.write("\n\n")
            f.write("\n\n")

            attr_fields = []

            for field_name, field in meta.fields_map.items():
                field_info = {}
                field_info["field_class"] = field.__class__.__name__
                field_info["name"] = field_name
                f.write(f"{field_name}\n")
                f.write('^' * len(field_name))
                f.write("\n\n")
                for slot in field.__slots__:
                    field_info[slot] = getattr(field, slot, None)
                attr_fields.append(field_info)

            print(attr_fields)

    #related_model = cls.apps[related_app_name][related_model_name]
    for app_name, models in Tortoise.apps.items():
        for model_name, model_class in models.items():
            write_model_rst(app_name, model_name, model_class)

async def run():
    try:
        await Tortoise.init(
            db_url='sqlite://:memory:',
            modules={'model': ['digicubes.storage.models']}
        )
        generate_model_documentation()

    finally:    
        await Tortoise.close_connections()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()

