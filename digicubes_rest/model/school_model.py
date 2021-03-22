# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
from datetime import datetime, date
import logging
from typing import List, Optional

from pydantic import BaseModel, PositiveInt, constr
from tortoise.exceptions import IntegrityError, MultipleObjectsReturned, ValidationError

from digicubes_rest.exceptions import ConstraintViolation, MutltipleObjectsError
from digicubes_rest.storage.models.school import School, Course, Unit

from .org_model import UserModel

logger = logging.getLogger()


class SchoolIn(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=School.NAME_LENGTH)]
    description: Optional[str]

    class Config:
        orm_mode = True

    async def create(self, **kwargs):
        try:
            db_school = await School.create(**self.dict(exclude_unset=True))
            return SchoolModel.from_orm(db_school)
        except (ValidationError, IntegrityError) as e:
            raise ConstraintViolation(str(e)) from e


class SchoolModel(SchoolIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(**kwargs) -> "SchoolModel":
        return await SchoolIn(**kwargs).create()

    @classmethod
    async def all(cls) -> List["SchoolModel"]:
        return [cls.from_orm(u) for u in await School.all()]

    @classmethod
    async def get(cls, **kwargs) -> "SchoolModel":
        try:
            orm_school = await School.get_or_none(**kwargs)
            return None if not orm_school else cls.from_orm(orm_school)
        except MultipleObjectsReturned as e:
            raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from e

    async def delete(self) -> None:
        await School.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_school = await School.get(id=self.id)
        school_in = SchoolIn(**kwargs)
        db_school.update_from_dict(school_in.dict(exclude_unset=True))
        await db_school.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_courses(self) -> List['CourseModel']:
        db_school = await School.get(id=self.id).only("id").prefetch_related("courses")
        return [CourseModel.from_orm(m) for m in db_school.courses]

    async def get_students(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("students")
        return [UserModel.from_orm(m) for m in db_school.students]

    async def get_teacher(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("teacher")
        return [UserModel.from_orm(m) for m in db_school.teacher]

    async def get_principals(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("principals")
        return [UserModel.from_orm(m) for m in db_school.principals]

    async def create_course(self, **kwargs) -> 'CourseModel':
        return await CourseModel.create(self, **kwargs)

# ----------------------------------------------------------------------
# CourseModel
# ----------------------------------------------------------------------


class CourseIn(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=Course.NAME_LENGTH)]
    is_private: Optional[bool]
    description: Optional[str]
    created_by_id: Optional[int]
    from_date: Optional[date]
    until: Optional[date]

    class Config:
        orm_mode = True

    async def create(self, school: SchoolModel) -> "CourseModel":
        try:
            params = self.dict(exclude_unset=True)
            params["school_id"] = school.id
            db_course = await Course.create(**params)
            return CourseModel.from_orm(db_course)
        except (ValidationError, IntegrityError) as e:
            raise ConstraintViolation(str(e)) from e


class CourseModel(CourseIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(school:SchoolModel, **kwargs) -> "CourseModel":
        return await CourseIn(**kwargs).create(school)

    @classmethod
    async def all(cls) -> List["CourseModel"]:
        return [cls.from_orm(u) for u in await Course.all()]

    @classmethod
    async def get(cls, **kwargs) -> "CourseModel":
        try:
            orm_course = await Course.get_or_none(**kwargs)
            return None if not orm_course else cls.from_orm(orm_course)
        except MultipleObjectsReturned as e:
            raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from e

    async def delete(self) -> None:
        await Course.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_course = await Course.get(id=self.id)
        course_in = CourseIn(**kwargs)
        db_course.update_from_dict(course_in.dict(exclude_unset=True))
        await db_course.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))
