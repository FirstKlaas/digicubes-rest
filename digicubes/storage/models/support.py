"""
Helper module with some use functions as well as the base model.
"""

import logging

from tortoise import fields
from tortoise.models import Model

logger = logging.getLogger(__name__)  # pylint: disable=C0103


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
        for field in cls.__public_fields__:
            if field in data:
                setattr(model, field, data[field])
        return model

    def unstructure(self, filtered_field_names=None):
        """
        Converts this object to an dict.
        The result contains onle keys that are in the ``filtered_field_names``
        list AND in the public field list of this class. A value of ``None``
        for the ``filtered_fields_name`` parameter means, all public fields
        should be converted.
        """
        result = {}
        meta = getattr(self, "_meta", None)
        if meta is None:
            return result

        public_fields = self.public_fields
        field_map = meta.fields_map
        if filtered_field_names is None:
            filtered_field_names = public_fields

        for field_name in filtered_field_names:
            if field_name in public_fields:
                field = field_map.get(field_name, None)
                if field is not None:
                    value = getattr(self, field_name)
                    if isinstance(field, (fields.DatetimeField, fields.DateField)):
                        result[field_name] = value.isoformat()
                    elif isinstance(field, fields.ManyToManyField):
                        logger.info("igoring relation %s", field_name)
                    elif isinstance(field, fields.ForeignKeyField):
                        logger.info("ignoring foreign key field %s", field_name)
                    else:
                        result[field_name] = value

        return result

    @property
    def public_fields(self):
        """
        List of public fields.

        The public field list by merging the ``__public_fields__`` class
        attribute of all classes in the class hierarchie.
        """
        calculated_fields = getattr(self.__class__, "__mro_public_fields__", None)
        if calculated_fields is not None:
            return calculated_fields

        result = []
        for cls in self.__class__.__mro__:
            result.extend(getattr(cls, "__public_fields__", []))

        setattr(self.__class__, "__mro_public_fields__", result)
        return result

    __public_fields__ = ["id", "created_at", "modified_at"]
    __updatable_fields__ = []
    __mro_public_fields__ = None

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods,missing-docstring
        abstract = True


class UUIDMixin:
    # pylint: disable=too-few-public-methods,missing-docstring

    uuid = fields.UUIDField()


class NamedMixin:
    # pylint: disable=too-few-public-methods,missing-docstring

<<<<<<< HEAD
    name = fields.CharField(32, unique=True, null=False)
=======
    name = fields.TextField(unique=True)
>>>>>>> b6b2b031cfa0cc3d475550033ea3bcd5c5d5073e

    @classmethod
    async def get_by_name(cls, name):
        """Get an instance of this class by its name attribute"""
        return await cls.filter(name=name).first()
