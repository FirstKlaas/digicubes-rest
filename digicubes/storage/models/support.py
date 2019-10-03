"""
Helper module with some use functions as well as the base model.
"""

import logging

from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from tortoise.fields import IntField, CharField, DatetimeField

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class BaseModel(Model):
    """
    This is the base model for all models in the digicube domain.
    """

    @classmethod
    def writable_fields(cls):
        """
        List of writable fields.
        """
        result = []
        for name, val in cls.__dict__.items():
            if isinstance(val, fields.Field):
                result.append(name)

        result.pop("id")
        return result

    def update(self, data):
        """
        Updates this instance with new values
        """
        for name in self.__class__.writable_fields():
            val = data.get(name, None)
            if val is not None:
                setattr(self, name, val)

    id: IntField = IntField(pk=True, description="Primary key")
    created_at: DatetimeField = DatetimeField(null=True, auto_now_add=True)
    modified_at: DatetimeField = DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods,missing-docstring
        abstract = True


class NamedMixin:
    # pylint: disable=too-few-public-methods,missing-docstring

    name = CharField(32, unique=True, null=False)

    @classmethod
    async def get_by_name(cls, name):
        """
        Get an instance of this class by its name attribute.
        If no such instance exists, returns None
        """
        try:
            return await cls.get(name=name)
        except DoesNotExist:
            return None
