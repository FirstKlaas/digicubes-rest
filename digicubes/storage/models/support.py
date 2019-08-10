"""
Helper module with some use functions as well as the base model.
"""

import logging

from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

from .fields import Info, IntField, CharField, DatetimeField

logger = logging.getLogger(__name__)  # pylint: disable=C0103

READONLY = Info(readable=True, writable=False)
WRITABLE = Info(readable=True, writable=True)
HIDDEN = Info(readable=False, writable=False)


class BaseModel(Model):
    """
    This is the base model for all models in the digicube domain.
    """

    @classmethod
    def structure(cls, data):
        """
        Creates an instance of this model based on a dictionary
        """
        model = cls()
        for field in cls.writable_fields():
            if field in data:
                setattr(model, field, data[field])
        return model

    @classmethod
    def writable_fields(cls):
        """
        List of writable fields.
        """
        result = []
        for name, val in cls.__dict__.items():
            if isinstance(val, fields.Field):
                info = getattr(val, "info", None)
                if info is not None and info.writable:
                    result.append(name)

        return result

    def update(self, data):
        """
        Updates this instance with new values
        """
        for name in self.__class__.writable_fields():
            val = data.get(name, None)
            if val is not None:
                setattr(self, name, val)

    def unstructure(self, filtered_field_names=None):
        """
        Converts this object to an dict.
        The result contains onle keys that are in the ``filtered_field_names``
        list AND in the public field list of this class. A value of ``None``
        for the ``filtered_fields_name`` parameter means, all public fields
        should be converted.
        """
        result = {}
        for name, val in self.__class__.__dict__.items():
            if filtered_field_names is None or name in filtered_field_names:
                if isinstance(val, fields.Field):
                    info = getattr(val, "info", None)
                    if info is not None and info.readable:
                        logger.debug(
                            "Converting %s to %s",
                            name,
                            info.convert(info, val, getattr(self, name)),
                        )
                        result[name] = info.convert(info, val, getattr(self, name))
        return result

    id: IntField = IntField(READONLY, pk=True, description="Primary key")
    created_at: DatetimeField = DatetimeField(READONLY, null=True, auto_now_add=True)
    modified_at: DatetimeField = DatetimeField(READONLY, null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods,missing-docstring
        abstract = True


class NamedMixin:
    # pylint: disable=too-few-public-methods,missing-docstring

    name = CharField(WRITABLE, 32, unique=True, null=False)

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
