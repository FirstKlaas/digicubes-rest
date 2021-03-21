# pylint: disable=redefined-outer-name
#
import logging
from typing import Generator

import pytest
from tortoise import Tortoise
from pydantic import ValidationError

from digicubes_rest.model import UserIn, UserModel, RoleModel, RoleIn, RightIn, RightModel
from digicubes_rest.storage.models import Role

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
async def orm() -> Generator:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"model": ["digicubes_rest.storage.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="function")
async def admin_user() -> UserModel:
    user = await UserModel.create(login="admin")
    yield user
    await user.delete()


@pytest.fixture(scope="function")
async def admin_role() -> RoleModel:
    role = await RoleModel.create(name="admin")
    yield role
    await role.delete()


@pytest.fixture
async def user_a() -> Generator:
    user = await UserModel.create(login="klaas")
    yield user
    await user.delete()


@pytest.mark.asyncio
async def test_create_user() -> None:
    # Check if we have no initial users
    users = await UserModel.all()
    assert len(users) == 0
    # Create a test user
    user = await UserModel.create(login="klaas")
    assert user.email is None, "Email is not None"
    # Check if we hav exactly one user
    users = await UserModel.all()
    assert len(users) == 1, "Expected exactly i user in the database"
    db_user = await UserModel.get(login="klaas")
    assert db_user.created_at is not None
    roles = await db_user.get_roles()
    assert len(roles) == 0


@pytest.mark.asyncio
async def test_update_user():
    user = UserIn(login="klaas", first_name="Klaas")
    user_out = await user.create()
    await user_out.update(first_name="Marion")
    user_changed = await UserModel.get(login="klaas")
    assert user_changed.first_name == "Marion"


@pytest.mark.asyncio
async def test_add_role_to_user(admin_role: RoleModel, admin_user: UserModel):
    assert admin_role.name == "admin"
    assert admin_user.login == "admin"
    roles = await admin_user.get_roles()
    assert len(roles) == 0
    await admin_user.add_role(admin_role)
    roles = await admin_user.get_roles()
    assert len(roles) == 1
    assert roles[0].name == "admin"

    # we can add the same role twice,
    # but the second call simply is
    # ignored. So the number of roles
    # doesn't change.
    await admin_user.add_role(admin_role)
    roles = await admin_user.get_roles()
    assert len(roles) == 1

    # Add new Role
    role_user = await RoleIn(name="user").create()
    await admin_user.add_role(role_user)
    roles = await admin_user.get_roles()
    assert len(roles) == 2

    # Delete the new role
    # Because an associated role has been deleted
    # the number of roles for this user should be
    # equal to one.
    await role_user.delete()
    roles = await admin_user.get_roles()
    assert len(roles) == 1

    users = await admin_role.get_users()
    assert len(users) == 1
    assert users[0].login == admin_user.login
    assert users[0].id == admin_user.id

    # Removing the last role
    await admin_user.remove_role(admin_role)
    roles = await admin_user.get_roles()
    assert len(roles) == 0

    users = await admin_role.get_users()
    assert len(users) == 0


@pytest.mark.asyncio
async def test_add_user_to_role(admin_role: RoleModel, admin_user: UserModel):
    assert admin_role.name == "admin"
    assert admin_user.login == "admin"

    users = await admin_role.get_users()
    assert len(users) == 0

    await admin_role.add_user(admin_user)
    users = await admin_role.get_users()
    assert len(users) == 1

    test_user = await UserIn(login="test").create()
    await admin_role.add_user(test_user)
    users = await admin_role.get_users()
    assert len(users) == 2

    await test_user.delete()
    users = await admin_role.get_users()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_role_creation():
    # No roles in db
    assert len(await RoleModel.all()) == 0

    # Create an admin role
    admin = await RoleIn(name="admin", description="THe admin of the cube").create()
    assert admin.created_at is not None
    assert admin.id is not None
    assert len(await RoleModel.all()) == 1
    await admin.delete()
    assert len(await RoleModel.all()) == 0
    # Field name is mandatory
    with pytest.raises(ValidationError):
        RoleIn()

    # Name length is restricted
    with pytest.raises(ValidationError):
        RoleIn(name="X" * (Role.NAME_LENGTH + 1))

    # Strip name automatically
    name = "   XXX   "
    role = await RoleIn(name=name).create()
    assert role.name == name.strip()


@pytest.mark.asyncio
async def test_add_right_to_role(admin_role: RoleModel):

    assert len(await RightModel.all()) == 0
    right_a = await RightIn(name="A").create()
    rights = await RightModel.all()
    assert len(rights) == 1
    assert rights[0].name == "A"
    await admin_role.add_right(right_a)
    rights = await admin_role.get_rights()
    assert len(rights) == 1
    right_b = await RightModel.create(name="B")
    assert right_b.name == "B"
    assert len(await RightModel.all()) == 2
