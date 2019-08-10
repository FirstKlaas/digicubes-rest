"""
School Module
"""
from tortoise.fields import ManyToManyField, ForeignKeyField

from .fields import DateField, BooleanField
from .support import BaseModel, NamedMixin, WRITABLE


class School(NamedMixin, BaseModel):
    """
    School Model
    """

    students = ManyToManyField("model.User", related_name="schools", through="school_user")
    # founder = ForeignKeyField("model.User", related_name="founder_of_schools", null=True)
    # principal = ForeignKeyField("model.User", related_name="principal_of", null=True)

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
    students = ManyToManyField("model.User", related_name="courses", through="course_student")
    school = ForeignKeyField("model.School", related_name="courses")
    created_by = ForeignKeyField("model.User", related_name="course_owner")
    teachers = ManyToManyField("model.User", related_name="lectures", through="teached_courses")
