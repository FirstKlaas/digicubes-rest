# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
from datetime import datetime
import logging
from typing import List, Optional

from pydantic import BaseModel, PositiveInt, constr
from tortoise.exceptions import IntegrityError, MultipleObjectsReturned, ValidationError

from digicubes_rest.exceptions import ConstraintViolation, MutltipleObjectsError
from digicubes_rest.storage.models.school import School, Course, Unit


logger = logging.getLogger()


class SchoolIn(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=School.NAME_LENGTH)]
    description: Optional[str]

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


# ----------------------------------------------------------------------
# CourseModel
# ----------------------------------------------------------------------

