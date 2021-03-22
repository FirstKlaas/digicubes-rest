# pylint: disable=redefined-outer-name
#
import pytest

import logging
from typing import Generator

from tortoise import Tortoise

from digicubes_rest.server import DigiCubeServer
from digicubes_rest.model import UserIn, UserModel

@pytest.fixture(scope="function", autouse=True)
async def orm() -> Generator:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"model": ["digicubes_rest.storage.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.fixture
def api():
    server = DigiCubeServer()
    yield server.api

@pytest.fixture
async def root() -> UserModel:
    user = await UserModel.create(
        login="root",
        is_active=True,
        is_verified=True)
    yield user
    await user.delete()

def test_hello_world(api, root: UserModel):
    data = {
        "login" : "root",
        "password" : "root"
    }
    r = api.requests.post("/login/", json=data)
    assert r.status_code == 200
