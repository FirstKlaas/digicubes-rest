# pylint: disable=redefined-outer-name, unused-argument
#
import pytest
import os
from multiprocessing import Process
from time import sleep
from typing import Generator
import logging

import requests
from tortoise import Tortoise

from digicubes_rest.server import DigiCubeServer
from digicubes_rest.storage.models import User
from digicubes_rest.model import UserModel
from digicubes_rest.storage import init_orm, create_schema, shutdown_orm


async def create_verified_account(login: str, password: str) -> User:
    user = await User.create(login=login, password=password, is_active=True, is_verified=True)
    user.password = password
    await user.save()
    return user


async def new_on_startup():
    os.environ["DIGICUBES_DATABASE_URL"] = "sqlite://:memory:"

    await init_orm()
    await create_schema()
    await create_verified_account("root", "root")


def run():
    dcs = DigiCubeServer()
    dcs.api.add_event_handler("startup", new_on_startup)
    dcs.run()


@pytest.fixture
def server() -> Generator:
    proc = Process(target=run, args=(), daemon=True)
    proc.start()
    sleep(1)
    yield
    proc.kill()  # Cleanup after test


@pytest.fixture
def token(server) -> str:
    data = {"login": "root", "password": "root"}
    resp = requests.post("http://127.0.0.1:3548/login/", json=data)
    token_data = resp.json()
    return token_data["bearer_token"]


@pytest.fixture
def headers(token) -> str:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def test_login(server):
    data = {"login": "root", "password": "root"}
    resp = requests.post("http://127.0.0.1:3548/login/", json=data)
    assert resp.status_code == 200
    token_data = resp.json()
    assert token_data is not None
    bearer_token = token_data["bearer_token"]
    assert bearer_token is not None


def test_token(token):
    assert token is not None


def test_users(headers):
    resp = requests.get("http://127.0.0.1:3548/users/", headers=headers)
    data = resp.json()
    assert "result" in data
    result = data["result"]
    assert len(result) == 1
    user = UserModel.parse_obj(result[0])
    assert user.login == "root"
    assert resp.status_code == 200
