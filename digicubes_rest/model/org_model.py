# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
from datetime import datetime
import logging
from typing import List, Optional

from pydantic import BaseModel, PositiveInt, constr
from tortoise.exceptions import IntegrityError, MultipleObjectsReturned, ValidationError

from digicubes_rest.exceptions import ConstraintViolation, MutltipleObjectsError
from digicubes_rest.storage.models.org import User, Role, Right

__all__ = ["UserIn", "UserOut", "RoleIn", "RoleOut"]

logger = logging.getLogger()

class UserIn(BaseModel):
    first_name: Optional[constr(strip_whitespace=True, max_length=User.FIRST_NAME_LENGHT)]
    last_name: Optional[constr(strip_whitespace=True, max_length=User.LAST_NAME_LENGHT)]
    login: Optional[constr(strip_whitespace=True, max_length=User.LOGIN_LENGHT)]
    email: Optional[constr(strip_whitespace=True, max_length=User.EMAIL_LENGHT)]
    is_active: Optional[bool]

    class Config:
        orm_mode = True

    async def create(self) -> "UserOut":
        try:
            db_user = await User.create(**self.dict(exclude_unset=True))
            return UserOut.from_orm(db_user)
        except (ValidationError, IntegrityError) as e:
            raise ConstraintViolation(str(e)) from e


class UserOut(UserIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]
    verified_at: Optional[datetime]
    is_verified: bool

    @staticmethod
    async def create(**kwargs) -> 'UserOut':
        return await UserIn(**kwargs).create()

    @classmethod
    async def all(cls) -> List["UserOut"]:
        return [cls.from_orm(u) for u in await User.all()]

    @classmethod
    async def get(cls, **kwargs) -> "UserOut":
        try:
            orm_user = await User.get_or_none(**kwargs)
            return None if not orm_user else cls.from_orm(orm_user)
        except MultipleObjectsReturned as e:
            raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from e

    async def delete(self) -> None:
        await User.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_user = await User.get(id=self.id)
        user_in = UserIn(**kwargs)
        db_user.update_from_dict(user_in.dict(exclude_unset=True))
        await db_user.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_roles(self) -> "RoleOut":
        user = await User.get(id=self.id).only("id").prefetch_related("roles")
        return [RoleOut.from_orm(r) for r in user.roles]

    async def add_role(self, role: "RoleOut") -> "UserOut":
        db_user = await User.get(id=self.id).only("id").prefetch_related("roles")
        await db_user.roles.add(await Role.get(id=role.id))
        return self

    async def remove_role(self, role: "RoleOut") -> "UserOut":
        db_user = await User.get(id=self.id).only("id").prefetch_related("roles")
        await db_user.roles.remove(await Role.get(id=role.id))
        return self

############################################################################
#  ROLE
############################################################################


class RoleIn(BaseModel):
    name: constr(strip_whitespace=True, max_length=Role.NAME_LENGTH)
    description: Optional[constr(strip_whitespace=True, max_length=Role.DESCRIPTION_LENGTH)]
    home_route: Optional[constr(strip_whitespace=True, max_length=Role.HOME_ROUTE_LENGTH)]

    class Config:
        orm_mode = True

    async def create(self) -> "RoleOut":
        try:
            db_role = await Role.create(**self.dict(exclude_unset=True))
            return RoleOut.from_orm(db_role)
        except (ValidationError, IntegrityError) as e:
            raise ConstraintViolation(str(e)) from e


class RoleOut(RoleIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(**kwargs) -> 'RoleOut':
        return await RoleIn(**kwargs).create()

    @classmethod
    async def all(cls) -> List["RoleOut"]:
        return [cls.from_orm(u) for u in await Role.all()]

    @classmethod
    async def get(cls, **kwargs) -> "RoleOut":
        try:
            orm_role = await Role.get_or_none(**kwargs)
            return None if not orm_role else cls.from_orm(orm_role)
        except MultipleObjectsReturned as e:
            raise MutltipleObjectsError(f"Multiple roles return for filter {kwargs}") from e

    async def delete(self) -> None:
        await Role.filter(id=self.id).only("id").delete()

    async def get_user(self) -> UserOut:
        role = await Role.get(id=self.id).only("id").prefetch_related("users")
        return [UserOut.from_orm(u) for u in role.users]

    async def update(self, **kwargs):
        db_role = await Role.get(id=self.id)
        role_in = RoleIn(**kwargs)
        db_role.update_from_dict(role_in.dict(exclude_unset=True))
        await db_role.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))


    async def get_rights(self) -> List["RightOut"]:
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        return [RightOut.from_orm(r) for r in db_role.rights]

    async def add_right(self, right: "RightOut") -> "RoleOut":
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        await db_role.rights.add(await Right.get(id=right.id))
        return self

    async def remove_right(self, right: "RightOut") -> "RoleOut":
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        await db_role.rights.remove(await Right.get(id=right.id))
        return self

    async def get_users(self) -> "UserOut":
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        return [UserOut.from_orm(r) for r in db_role.users]

    async def add_user(self, user: "UserOut") -> "RoleOut":
        """
        Add user to role.
        """
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        await db_role.users.add(await User.get(id=user.id))
        return self

    async def remove_user(self, user: "UserOut") -> "RoleOut":
        """
        Remove user from role.
        """
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        await db_role.users.remove(await User.get(id=user.id))
        return self

############################################################################
#  RIGHT
############################################################################


class RightIn(BaseModel):
    name: constr(strip_whitespace=True, max_length=Right.NAME_LENGTH)
    description: Optional[constr(strip_whitespace=True, max_length=Right.DESCRIPTION_LENGTH)]

    class Config:
        orm_mode = True

    async def create(self) -> "RightOut":
        try:
            db_right = await Right.create(**self.dict(exclude_unset=True))
            return RightOut.from_orm(db_right)
        except (ValidationError, IntegrityError) as e:
            raise ConstraintViolation(str(e)) from e


class RightOut(RightIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(**kwargs) -> 'RightOut':
        return await RightIn(**kwargs).create()

    @classmethod
    async def all(cls) -> List["RightOut"]:
        return [cls.from_orm(u) for u in await Right.all()]

    @classmethod
    async def get(cls, **kwargs) -> "RightOut":
        try:
            orm_right = await Right.get_or_none(**kwargs)
            return None if not orm_right else cls.from_orm(orm_right)
        except MultipleObjectsReturned as e:
            raise MutltipleObjectsError(f"Multiple roles return for filter {kwargs}") from e

    async def delete(self) -> None:
        await Right.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_right = await Right.get(id=self.id)
        right_in = RightIn(**kwargs)
        db_right.update_from_dict(right_in.dict(exclude_unset=True))
        await db_right.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_roles(self) -> "RoleOut":
        right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        return [RoleOut.from_orm(r) for r in right.roles]

    async def add_role(self, role: "RoleOut") -> "RightOut":
        db_right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        await db_right.roles.add(await Role.get(id=role.id))
        return self

    async def remove_role(self, role: "RoleOut") -> "RightOut":
        db_right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        await db_right.roles.remove(await Role.get(id=role.id))
        return self
