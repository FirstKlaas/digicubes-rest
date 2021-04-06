# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
import logging
from datetime import date, datetime
from typing import List, Optional, TypeVar

from pydantic import PositiveInt, constr
from tortoise.exceptions import (FieldError, IntegrityError,
                                 MultipleObjectsReturned, ValidationError)
from tortoise.query_utils import Prefetch

from digicubes_rest.exceptions import (ConstraintViolation,
                                       MutltipleObjectsError, QueryError)
from digicubes_rest.storage.models.school import Course, School, Unit

from .abstract_base import ResponseModel
from .org_model import UserModel

logger = logging.getLogger()

__all__ = [
    "SchoolModel",
    "CourseModel",
    "UnitModel",
    "SchoolListModel",
    "CourseListModel",
    "UnitListModel",
]

SCHOOL = TypeVar("SCHOOL", bound="SchoolModel")
SCHOOLS = TypeVar("SCHOOLS", bound="SchoolListModel")
COURSE = TypeVar("COURSE", bound="CourseModel")
COURSES = TypeVar("COURSES", bound="CourseListModel")
UNIT = TypeVar("UNIT", bound="UnitModel")
UNITS = TypeVar("UNITS", bound="UnitListModel")


class SchoolIn(ResponseModel):
    name: Optional[constr(strip_whitespace=True, max_length=School.NAME_LENGTH)]
    description: Optional[str]

    class Config:
        orm_mode = True

    async def create(self):
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
    async def create(**kwargs) -> SCHOOL:
        return await SchoolIn(**kwargs).create()

    @staticmethod
    def list_model(items: List[SCHOOL]) -> SCHOOLS:
        return SchoolListModel(__root__=items)

    @staticmethod
    async def orm_create_from_obj(data) -> SCHOOL:
        return await SchoolIn.parse_obj(data).create()

    @classmethod
    async def all(cls) -> List[SCHOOL]:
        return [cls.from_orm(u) for u in await School.all()]

    @classmethod
    async def get(cls, **kwargs) -> SCHOOL:
        try:
            orm_school = await School.get_or_none(**kwargs)
            return None if not orm_school else cls.from_orm(orm_school)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(
                f"Multiple user returned for given filter {kwargs}"
            ) from error

    async def delete(self) -> None:
        await School.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_school = await School.get(id=self.id)
        school_in = SchoolIn(**kwargs)
        db_school.update_from_dict(school_in.dict(exclude_unset=True))
        await db_school.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_students(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("students")
        return [UserModel.from_orm(m) for m in db_school.students]

    async def get_teacher(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("teacher")
        return [UserModel.from_orm(m) for m in db_school.teacher]

    async def get_principals(self) -> List[UserModel]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("principals")
        return [UserModel.from_orm(m) for m in db_school.principals]

    async def create_course(self, **kwargs) -> COURSE:
        return await CourseModel.create(self, **kwargs)

    async def find_courses(self, **kwargs) -> List[COURSE]:
        try:
            school = await School.get(id=self.id).prefetch_related(
                Prefetch("courses", queryset=Course.filter(**kwargs))
            )
            return [CourseModel.from_orm(course) for course in school.courses]

        except FieldError as error:
            raise QueryError(str(error)) from error

    async def get_courses(self) -> List[COURSE]:
        db_school = await School.get(id=self.id).only("id").prefetch_related("courses")
        return [CourseModel.from_orm(m) for m in db_school.courses]


class SchoolListModel(ResponseModel):
    __root__: List[SchoolModel]


# ----------------------------------------------------------------------
# CourseModel
# ----------------------------------------------------------------------


class CourseIn(ResponseModel):
    school_id: Optional[int]
    name: Optional[constr(strip_whitespace=True, max_length=Course.NAME_LENGTH)]
    is_private: Optional[bool]
    description: Optional[str]
    created_by_id: Optional[int]
    from_date: Optional[date]
    until_date: Optional[date]

    class Config:
        orm_mode = True

    async def create(self, school_id: int) -> COURSE:
        try:
            self.school_id = school_id
            params = self.dict(exclude_unset=True)
            db_course = await Course.create(**params)
            return CourseModel.from_orm(db_course)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    async def get_school(self) -> SchoolModel:
        return await SchoolModel.get(id=self.school_id)

    async def create_unit(self, **kwargs) -> UNIT:
        return await UnitModel.create(self, **kwargs)


class CourseModel(CourseIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(school_id: int, **kwargs) -> COURSE:
        return await CourseIn(**kwargs).create(school_id)

    @staticmethod
    def list_model(items: List[COURSE]) -> COURSES:
        return CourseListModel(__root__=items)

    @staticmethod
    async def orm_create_from_obj(school_id: int, data) -> COURSE:
        return await CourseIn.parse_obj(data).create(school_id=school_id)

    @classmethod
    async def all(cls) -> List[COURSE]:
        return [cls.from_orm(u) for u in await Course.all()]

    @classmethod
    async def get(cls, **kwargs) -> COURSE:
        try:
            orm_course = await Course.get_or_none(**kwargs)
            return None if not orm_course else cls.from_orm(orm_course)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(f"Multiple user return for filter {kwargs}") from error

    async def delete(self) -> None:
        await Course.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_course = await Course.get(id=self.id)
        course_in = CourseIn(**kwargs)
        db_course.update_from_dict(course_in.dict(exclude_unset=True))
        await db_course.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))

    async def get_units(self) -> List[UNIT]:
        db_course = await Course.get(id=self.id).only("id").prefetch_related("units")
        return [UnitModel.from_orm(m) for m in db_course.units]

    async def find_units(self, **kwargs) -> List[UNIT]:
        try:
            course = await Course.get(id=self.id).prefetch_related(
                Prefetch("units", queryset=Unit.filter(**kwargs))
            )
            return [UnitModel.from_orm(unit) for unit in course.units]

        except FieldError as error:
            raise QueryError(str(error)) from error

    async def create_unit(self, **kwargs) -> UNIT:
        return await UnitModel.create(self, **kwargs)


class CourseListModel(ResponseModel):
    __root__: List[CourseModel]


# ----------------------------------------------------------------------
# UnitModel
# ----------------------------------------------------------------------


class UnitIn(ResponseModel):

    course_id: Optional[PositiveInt]
    name: Optional[constr(strip_whitespace=True, max_length=Unit.NAME_LENGTH)]
    position: Optional[int]
    is_active: Optional[bool]
    is_visible: Optional[bool]
    short_description: Optional[constr(strip_whitespace=True, max_length=Unit.DESCRIPTION_LENGTH)]
    long_description: Optional[str]

    class Config:
        orm_mode = True

    async def create(self, course_id: int) -> UNIT:
        try:
            self.course_id = course_id
            params = self.dict(exclude_unset=True, exclude_none=True)
            db_unit = await Unit.create(**params)
            return UnitModel.from_orm(db_unit)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    async def get_Course(self) -> CourseModel:
        return await CourseModel.get(id=self.course_id)


class UnitModel(UnitIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(course_id: int, **kwargs) -> UNIT:
        return await UnitIn(**kwargs).create(course_id)

    @staticmethod
    def list_model(items: List[UNIT]) -> UNITS:
        return UnitListModel(__root__=items)

    @staticmethod
    async def orm_create_from_obj(course_id: int, data) -> UNIT:
        return await UnitIn.parse_obj(data).create(course_id)

    @classmethod
    async def all(cls) -> List[UNIT]:
        return [cls.from_orm(u) for u in await Unit.all()]

    @classmethod
    async def get(cls, **kwargs) -> UNIT:
        try:
            orm_unit = await Unit.get_or_none(**kwargs)
            return None if not orm_unit else cls.from_orm(orm_unit)
        except MultipleObjectsReturned as error:
            raise MutltipleObjectsError(f"Multiple units return for filter {kwargs}") from error

    async def delete(self) -> None:
        await Unit.filter(id=self.id).only("id").delete()

    async def update(self, **kwargs):
        db_unit = await Unit.get(id=self.id)
        unit_in = UnitIn(**kwargs)
        db_unit.update_from_dict(unit_in.dict(exclude_unset=True))
        await db_unit.save()

    async def refresh(self):
        self.update_from_obj(await self.get(id=self.id))


class UnitListModel(ResponseModel):
    __root__: List[UnitModel]
