"""
School Module
"""
from tortoise import fields

from .support import BaseModel, NamedMixin


class School(NamedMixin, BaseModel):
    """
    School Model
    """

    __updatable_fields__ = ["name"]
    __public_fields__ = __updatable_fields__

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "school"

    def __str__(self):
        return self.name


class Course(NamedMixin, BaseModel):
    """
    Cource Model
    """

    from_date = fields.DateField()
    until_date = fields.DateField()
    is_private = fields.BooleanField(default=False)
    students = fields.ManyToManyField("model.User", related_name="courses", through="student")
    school = fields.ForeignKeyField("model.School", related_name="courses")
