from tortoise import fields

from .support import BaseModel, NamedMixin

class School(NameMixin, BaseModel):

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "school"


class Course(NameMixin, BaseModel):

    from_date = fields.DateField()
    until_date = fields.DateField()
    is_private = fields.BooleanField(default=False)  
    students = fields.ManyToManyField('model.User', related_name='courses', through='student')  
