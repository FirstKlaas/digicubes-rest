"""
School Module
"""
from typing import Dict, Any

from tortoise.fields import (
    ManyToManyField,
    TextField,
    DateField,
    BooleanField,
    IntField,
)
from .support import BaseModel, NamedMixin

PropertyData = Dict[str, Any]


class School(NamedMixin, BaseModel):
    """
    School Model
    """

    description = TextField(default="")

    students = ManyToManyField("model.User", related_name="schools", through="school_user")
    principals = ManyToManyField(
        "model.User", related_name="principals", through="school_principal"
    )
    teachers = ManyToManyField("model.User", related_name="teachers", through="school_teachers")

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "school"

    def __str__(self):
        return self.name

    @staticmethod
    async def create_from(data: PropertyData):
        """
        Converts the data into an school instance and
        creates it directly.
        """
        school = await School.create(
            name=data.get("name", None), description=data.get("description", "")
        )
        return school


class Course(NamedMixin, BaseModel):
    """
    Course Model
    """

    is_private = BooleanField(default=False)
    description = TextField(default="")
    school_id = IntField(null=True)
    created_by_id = IntField(null=True)
    from_date = DateField(null=True)

    # students = ManyToManyField("model.User", related_name="courses", through="course_students")
    # teachers = ManyToManyField(
    #    "model.User", related_name="course_teachers", through="course_teachers"
    # )

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "course"

    def __str__(self):
        return self.name
