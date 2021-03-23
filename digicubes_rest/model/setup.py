import asyncio as aio
import logging


from tortoise import Tortoise

from digicubes_rest.model import UserModel, RightModel, RoleModel
from digicubes_rest.storage import init_orm, create_schema, shutdown_orm

logger = logging.getLogger(__name__)

template = {
    "rights": [
        "no_limits",
        "user_create",
        "user_read",
        "user_update",
        "user_delete",
        "user_verify",
        "user_activate",
        "school_create",
        "school_read",
        "school_update",
        "school_delete",
        "course_create",
        "course_read",
        "course_update",
        "course_delete",
        "unit_create",
        "unit_read",
        "unit_update",
        "unit_delete",
    ],
    "roles": [
        {
            "name": "root",
            "description": "Great power leads to great responsibility",
            "rights": ["no_limits"],
        },
        {
            "name": "admin",
            "description": "Manage most of the entities",
            "rights": [
                "school_create",
                "school_update",
                "school_delete",
                "user_verify",
                "user_activate",
            ],
        },
        {
            "name": "headmaster",
            "description": "You are the headmaster of one or more schools.",
            "rights": ["school_read", "course_create", "course_read", "course_update"],
        },
        {
            "name": "teacher",
            "description": "People can learn so much from you.",
            "rights": [
                "school_read",
                "course_read",
                "course_update",
                "course_create",
                "unit_create",
                "unit_read",
                "unit_update",
                "unit_delete",
            ],
        },
        {
            "name": "student",
            "description": "You are a DigiCube Hero. Go and explore something new.",
            "rights": ["school_read", "course_read", "unit_read"],
        },
    ],
}


async def setup_base_model():
    """
    Creating the very basic elements needed to get up and running. This
    should only be called after a fresh installation.

    If the database already contains a root account, no changes will be made.
    """

    try:
        # Init ORM
        await init_orm()
        await create_schema()

        # Check for root account
        root = await UserModel.get(login="root")
        if root is not None:
            logger.info("Root account already exists. No changes will be made.")
            return

        # No root account. So we will setup the basics.
        # Starting with the root account
        root = await UserModel.create(login="root", is_active=True, is_verified=True)
        await root.set_password("digicubes")

        rights = {}
        roles = {}

        # Now setup the rights and store the created elements
        # in a dictionary
        for right in template["rights"]:
            rights[right] = await RightModel.create(name=right)

        logger.info("%d rights created.", len(await RightModel.all()))

        # Now setup the roles with the appropriate rights
        for role in template["roles"]:
            db_role = await RoleModel.create(name=role["name"], description=role["description"])
            logger.info("Creating role %s with %d right(s)", db_role.name, len(role["rights"]))
            for right in role["rights"]:
                await db_role.add_right(rights[right])
            roles[db_role.name] = db_role

    finally:
        await shutdown_orm()


def run():
    aio.run(setup_base_model())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    aio.run(setup_base_model())
