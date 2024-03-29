"""
School Module
"""
from typing import Any, Dict

from tortoise import fields

from .support import BaseModel, NamedMixin

PropertyData = Dict[str, Any]


class School(NamedMixin, BaseModel):
    """
    School Model

    """

    description = fields.TextField(default="")

    students = fields.ManyToManyField(
        "model.User", related_name="student_schools", through="school_student"
    )

    principals = fields.ManyToManyField(
        "model.User",
        related_name="principal_schools",
        through="school_principal",
    )

    teacher = fields.ManyToManyField(
        "model.User", related_name="teacher_schools", through="school_teacher"
    )

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "school"

    def __str__(self):
        return str(self.name)

    @staticmethod
    async def create_from(data: PropertyData):
        """
        Converts the data into an school instance and
        creates it directly.
        """
        school = await School.create(
            name=data.get("name", None),
            description=data.get("description", ""),
        )
        return school


class Course(BaseModel):
    """
    Course Model

    A course is connected to a school, The name of the course is unique
    within the school. This can not be expressed in tortoise orm and
    must be handeled in the higher layer.

    A course has 0 or more units.
    """

    NAME_LENGTH = 32
    name = fields.CharField(NAME_LENGTH, null=False)
    is_private = fields.BooleanField(default=False)
    description = fields.TextField(default="")
    created_by_id = fields.IntField(null=True)
    from_date = fields.DateField(null=True)
    until_date = fields.DateField(null=True)

    school = fields.ForeignKeyField("model.School", related_name="courses")

    students = fields.ManyToManyField(
        "model.User", related_name="courses", through="course_students"
    )

    teachers = fields.ManyToManyField(
        "model.User", related_name="course_teachers", through="course_teachers"
    )

    units: fields.ReverseRelation["Unit"]

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "course"

    def __str__(self):
        return str(self.name)


class Unit(BaseModel):
    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "unit"

    DESCRIPTION_LENGTH = 64
    NAME_LENGTH = 32

    course: fields.ForeignKeyRelation[Course] = fields.ForeignKeyField(
        "model.Course", related_name="units"
    )

    name = fields.CharField(NAME_LENGTH, null=False)
    position = fields.IntField(null=False, default="-1")

    is_active = fields.BooleanField(default=False)
    is_visible = fields.BooleanField(default=False)

    short_description = fields.CharField(DESCRIPTION_LENGTH, null=False, default="")
    long_description = fields.TextField(null=False, default="")
