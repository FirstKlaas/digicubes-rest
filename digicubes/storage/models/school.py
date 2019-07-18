"""
School Module
"""
from tortoise.fields import ManyToManyField, ForeignKeyField

from .fields import DateField, BooleanField
from .support import BaseModel, NamedMixin, READONLY, WRITABLE

class School(NamedMixin, BaseModel):
    """
    School Model
    """

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

    from_date = DateField(WRITABLE)
    until_date = DateField(WRITABLE)
    is_private = BooleanField(WRITABLE, default=False)
    students = ManyToManyField("model.User", related_name="courses", through="student")
    school = ForeignKeyField("model.School", related_name="courses")
