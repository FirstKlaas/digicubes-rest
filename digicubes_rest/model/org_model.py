# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
from datetime import datetime
import logging
from typing import List, Optional, TypeVar

from pydantic import BaseModel, PositiveInt, constr, parse_obj_as
from tortoise.exceptions import IntegrityError, MultipleObjectsReturned, ValidationError

from digicubes_rest.exceptions import ConstraintViolation, MutltipleObjectsError
from digicubes_rest.storage.models.org import User, Role, Right

__all__ = ["UserModel", "RoleModel"]

logger = logging.getLogger()

USER = TypeVar("USER", bound="UserModel")
ROLE = TypeVar("ROLE", bound="RoleModel")
ROLES = TypeVar("ROLES", bound="RoleListModel")
RIGHT = TypeVar("RIGHT", bound="RightModel")


class UserModelCreate(BaseModel):
    first_name: Optional[constr(strip_whitespace=True, max_length=User.FIRST_NAME_LENGHT)]
    last_name: Optional[constr(strip_whitespace=True, max_length=User.LAST_NAME_LENGHT)]
    login: constr(strip_whitespace=True, max_length=User.LOGIN_LENGHT)
    email: constr(strip_whitespace=True, max_length=User.EMAIL_LENGHT)
    password: Optional[str]
    is_active: Optional[bool]
    is_verified: Optional[bool]

    class Config:
        orm_mode = True

class UserModel(BaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    verified_at: Optional[datetime]

    first_name: Optional[constr(strip_whitespace=True, max_length=User.FIRST_NAME_LENGHT)]
    last_name: Optional[constr(strip_whitespace=True, max_length=User.LAST_NAME_LENGHT)]
    login: Optional[constr(strip_whitespace=True, max_length=User.LOGIN_LENGHT)]
    email: Optional[constr(strip_whitespace=True, max_length=User.EMAIL_LENGHT)]
    is_active: Optional[bool]
    is_verified: Optional[bool]

    class Config:
        orm_mode = True

    @staticmethod
    async def create(**kwargs) -> USER:
        user = UserModel(**kwargs)
        try:
            db_user = await User.create(**user.dict(exclude_unset=True, exclude_none=True))
            return UserModel.from_orm(db_user)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    @staticmethod
    async def create_from_json(data) -> USER:
        try:
            user = UserModel.parse_raw(data)
            user.id = None
            user.created_at = datetime.utcnow()
            user.modified_at = datetime.utcnow()
            db_user = await User.create(**user.dict(exclude_unset=True, exclude_none=True))
            return UserModel.from_orm(db_user)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    @classmethod
    async def all(cls) -> List[USER]:
        return [cls.from_orm(u) for u in await User.all()]

    @classmethod
    async def get(cls, **kwargs) -> USER:
        try:
            orm_user = await User.get_or_none(**kwargs)
            return None if not orm_user else cls.from_orm(orm_user)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from error

    async def set_password(self, password: str):
        db_user = await User.get(id=self.id)
        db_user.password = password
        await db_user.save()

    async def delete(self) -> None:
        await User.filter(id=self.id).only("id").delete()

    async def update(self):
        db_user = await User.get(id=self.id)
        self.modified_at = datetime.utcnow()
        db_user.update_from_dict(self.dict(exclude_unset=True, exclude_none=True))
        await db_user.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_roles(self) -> ROLES:
        try:
            user = await User.get(id=self.id).only("id").prefetch_related("roles")
            return RoleListModel(__root__=[RoleModel.from_orm(role) for role in user.roles])
        except Exception as error:
            raise AttributeError(str(error)) from error

    async def add_role(self, role: ROLE) -> USER:
        db_user = await User.get(id=self.id).only("id").prefetch_related("roles")
        await db_user.roles.add(await Role.get(id=role.id))
        return self

    async def remove_role(self, role: ROLE) -> USER:
        db_user = await User.get(id=self.id).only("id").prefetch_related("roles")
        await db_user.roles.remove(await Role.get(id=role.id))
        return self


############################################################################
#  ROLE
############################################################################

class RoleModel(BaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    name: constr(strip_whitespace=True, max_length=Role.NAME_LENGTH)
    description: Optional[constr(strip_whitespace=True, max_length=Role.DESCRIPTION_LENGTH)]
    home_route: Optional[constr(strip_whitespace=True, max_length=Role.HOME_ROUTE_LENGTH)]

    class Config:
        orm_mode = True

    @staticmethod
    async def create(**kwargs) -> ROLE:
        role = RoleModel(**kwargs)
        try:
            db_role = await Role.create(**role.dict(exclude_unset=True, exclude_none=True))
            return RoleModel.from_orm(db_role)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    @classmethod
    async def all(cls) -> List[ROLE]:
        return [cls.from_orm(u) for u in await Role.all()]

    @classmethod
    async def get(cls, **kwargs) -> ROLE:
        try:
            orm_role = await Role.get_or_none(**kwargs)
            return None if not orm_role else cls.from_orm(orm_role)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(f"Multiple roles return for filter {kwargs}") from error

    async def delete(self) -> None:
        await Role.filter(id=self.id).only("id").delete()

    async def get_user(self) -> UserModel:
        role = await Role.get(id=self.id).only("id").prefetch_related("users")
        return [UserModel.from_orm(u) for u in role.users]

    async def update(self, **kwargs):
        db_role = await Role.get(id=self.id)
        role = RoleModel(**kwargs)
        role.id = None  # pylint: disable=invalid-name
        role.created_at = None
        role.modified_at = datetime.utcnow()
        db_role.update_from_dict(role.dict(exclude_unset=True, exclude_none=True))
        await db_role.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_rights(self) -> List[RIGHT]:
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        return [RightModel.from_orm(r) for r in db_role.rights]

    async def add_right(self, right: RIGHT) -> ROLE:
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        await db_role.rights.add(await Right.get(id=right.id))
        return self

    async def remove_right(self, right: RIGHT) -> ROLE:
        db_role = await Role.get(id=self.id).only("id").prefetch_related("rights")
        await db_role.rights.remove(await Right.get(id=right.id))
        return self

    async def get_users(self) -> USER:
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        return [UserModel.from_orm(r) for r in db_role.users]

    async def add_user(self, user: USER) -> ROLE:
        """
        Add user to role.
        """
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        await db_role.users.add(await User.get(id=user.id))
        return self

    async def remove_user(self, user: USER) -> ROLE:
        """
        Remove user from role.
        """
        db_role = await Role.get(id=self.id).only("id").prefetch_related("users")
        await db_role.users.remove(await User.get(id=user.id))
        return self

class RoleListModel(BaseModel):
    __root__: List[RoleModel]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    class Config:
        orm_mode = True

############################################################################
#  RIGHT
############################################################################


class RightModel(BaseModel):
    id: Optional[PositiveInt]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    name: constr(strip_whitespace=True, max_length=Right.NAME_LENGTH)
    description: Optional[constr(strip_whitespace=True, max_length=Right.DESCRIPTION_LENGTH)]

    class Config:
        orm_mode = True

    @staticmethod
    async def create(**kwargs) -> RIGHT:
        right = RightModel(**kwargs)
        right.id = None  # pylint: disable=invalid-name
        right.created_at = None
        try:
            db_right = await Right.create(**right.dict(exclude_unset=True, exclude_none=True))
            return RightModel.from_orm(db_right)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    @classmethod
    async def all(cls) -> List[RIGHT]:
        return [cls.from_orm(u) for u in await Right.all()]

    @classmethod
    async def get(cls, **kwargs) -> RIGHT:
        try:
            orm_right = await Right.get_or_none(**kwargs)
            return None if not orm_right else cls.from_orm(orm_right)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(f"Multiple roles return for filter {kwargs}") from error

    async def delete(self) -> None:
        await Right.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_right = await Right.get(id=self.id)
        right = RightModel(**kwargs)
        right.id = None
        right.created_at = None
        db_right.update_from_dict(right.dict(exclude_unset=True, exclude_none=True))
        await db_right.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_roles(self) -> ROLE:
        right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        return [RoleModel.from_orm(r) for r in right.roles]

    async def add_role(self, role: ROLE) -> RIGHT:
        db_right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        await db_right.roles.add(await Role.get(id=role.id))
        return self

    async def remove_role(self, role: ROLE) -> RIGHT:
        db_right = await Right.get(id=self.id).only("id").prefetch_related("roles")
        await db_right.roles.remove(await Role.get(id=role.id))
        return self
