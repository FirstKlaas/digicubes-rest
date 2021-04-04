# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
import logging
from datetime import date, datetime
from typing import List, Optional

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

    async def create_course(self, **kwargs) -> "CourseModel":
        return await CourseModel.create(self, **kwargs)

    async def find_courses(self, **kwargs) -> List["CourseModel"]:
        try:
            school = await School.get(id=self.id).prefetch_related(
                Prefetch("courses", queryset=Course.filter(**kwargs))
            )
            return [CourseModel.from_orm(course) for course in school.courses]

        except FieldError as error:
            raise QueryError(str(error)) from error

    async def get_courses(self) -> List["CourseModel"]:
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
    until: Optional[date]

    class Config:
        orm_mode = True

    async def create(self, school: SchoolModel) -> "CourseModel":
        try:
            self.school_id = school.id
            params = self.dict(exclude_unset=True)
            db_course = await Course.create(**params)
            return CourseModel.from_orm(db_course)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    async def get_school(self) -> SchoolModel:
        return await SchoolModel.get(id=self.school_id)

    async def create_unit(self, **kwargs) -> "UnitModel":
        return await UnitModel.create(self, **kwargs)


class CourseModel(CourseIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(school: SchoolModel, **kwargs) -> "CourseModel":
        return await CourseIn(**kwargs).create(school)

    @classmethod
    async def all(cls) -> List["CourseModel"]:
        return [cls.from_orm(u) for u in await Course.all()]

    @classmethod
    async def get(cls, **kwargs) -> "CourseModel":
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

    async def get_units(self) -> List["UnitModel"]:
        db_course = await Course.get(id=self.id).only("id").prefetch_related("units")
        return [UnitModel.from_orm(m) for m in db_course.units]

    async def find_units(self, **kwargs) -> List["UnitModel"]:
        try:
            course = await Course.get(id=self.id).prefetch_related(
                Prefetch("units", queryset=Unit.filter(**kwargs))
            )
            return [UnitModel.from_orm(unit) for unit in course.units]

        except FieldError as error:
            raise QueryError(str(error)) from error

    async def create_unit(self, **kwargs) -> "UnitModel":
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

    async def create(self, course: CourseModel) -> "UnitModel":
        try:
            self.course_id = course.id
            params = self.dict(exclude_unset=True)
            db_unit = await Unit.create(**params)
            return UnitModel.from_orm(db_unit)
        except (ValidationError, IntegrityError) as error:
            raise ConstraintViolation(str(error)) from error

    async def get_Course(self):
        return await CourseModel.get(id=self.course_id)


class UnitModel(UnitIn):
    id: PositiveInt
    created_at: datetime
    modified_at: Optional[datetime]

    @staticmethod
    async def create(course: CourseModel, **kwargs) -> "UnitModel":
        return await UnitIn(**kwargs).create(course)

    @classmethod
    async def all(cls) -> List["UnitModel"]:
        return [cls.from_orm(u) for u in await Unit.all()]

    @classmethod
    async def get(cls, **kwargs) -> "UnitModel":
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
