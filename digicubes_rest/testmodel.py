"""
Pydantic Based Datamodel

(C) FirstKlaas 2021
"""
import asyncio as aio
from typing import List

from pydantic import BaseModel
from tortoise import Tortoise, Model
from tortoise.exceptions import MultipleObjectsReturned
from tortoise.fields import CharField
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from digicubes_rest.model import UserIn, UserOut
from digicubes_rest.exceptions import MutltipleObjectsError

"""
async def create_user(user: User.In) -> User.Out:
    return await User.create(**user.dict(exclude_unset=True))

async def get_users() -> List[User.Out] :
    return [User.Out.from_orm(u) for u in await User.all()]

async def get_user(**kwargs) -> User.Out:
    try:
        orm_user = await User.get_or_none(**kwargs)
        return None if not orm_user else User.Out.from_orm(orm_user)
    except MultipleObjectsReturned as e:
        raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from e
"""


async def init_orm():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"model": ["digicubes_rest.storage.models"]},
    )
    await Tortoise.generate_schemas(safe=True)


async def run():
    try:
        await init_orm()
        await UserIn(login="klaas", first_name="Klaas", last_name="Nebuhr").create()
        await UserIn(
            login="marion", first_name="Marion", last_name="Nebuhr", email="marion@nebuhr.de"
        ).create()
        u2 = await UserOut.get(last_name="Nebuhr", first_name="Marion")
        print(u2)
        print(await UserOut.all())
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    print("Start")
    aio.run(run())
