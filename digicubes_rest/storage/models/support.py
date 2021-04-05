"""
Helper module with some use functions as well as the base model.
"""

import logging

from tortoise.fields import CharField, DatetimeField, IntField
from tortoise.models import Model

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class BaseModel(Model):
    """
    This is the base model for all models in the digicube domain.
    """

    id: IntField = IntField(pk=True, description="Primary key")
    created_at: DatetimeField = DatetimeField(null=True, auto_now_add=True)
    modified_at: DatetimeField = DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods,missing-docstring
        abstract = True


class NamedMixin:
    # pylint: disable=too-few-public-methods,missing-docstring

    NAME_LENGTH = 32

    name = CharField(NAME_LENGTH, unique=True, null=False)

    @classmethod
    async def get_by_name(cls, name):
        """
        Get an instance of this class by its name attribute.
        If no such instance exists, returns None
        """
        return await cls.get_or_None(name=name)
