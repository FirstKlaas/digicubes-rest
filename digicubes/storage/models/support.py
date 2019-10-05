"""
Helper module with some use functions as well as the base model.
"""

import logging

from tortoise import fields, Tortoise, transactions
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.models import Model, ModelMeta

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
            if name != "id" and isinstance(val, fields.Field):
                result.append(name)

        return result

    @classmethod
    def structure(cls, data):
        """
        Creates a new instance of cls and sets
        the values based on data.
        """
        meta = Tortoise.describe_model(cls)
        obj = cls()
        for field in meta["data_fields"]:
            name = field["name"]
            # python_type = field["python_type"]
            if name in data:
                setattr(obj, name, data[name])
        return obj

    @classmethod
    async def create_ressource(cls, data, filter_fields=None):
        # pylint: disable=too-many-return-statements
        """
        Generic ressource creation.
        All properties from data, which match an data field name
        from the model, will be transfered to a new instance.
        All other key value pairs are ignored.

        The new ressource or the newly created ressources are
        saved to the database. In case of an bulk creation, the
        operation is atomic. If one ressource fails to create, no
        ressource will be created.
        """
        if not isinstance(cls, ModelMeta):
            raise ValueError(
                "Parameter cls expected to be of type ModelMeta. But type is %s" % type(cls)
            )

        transaction = await transactions.start_transaction()
        try:
            if isinstance(data, dict):
                logger.info("Creating ressource for class %s.", cls)
                res = cls.structure(data)
                await res.save()
                await transaction.commit()
                return (201, res.unstructure(filter_fields))

            if isinstance(data, list):
                # Bulk creation of schools
                res = [cls.structure(item) for item in data]
                await cls.bulk_create(res)
                await transaction.commit()
                return (201, None)

            await transaction.rollback()
            return (500, f"Unsupported data type {type(data)}")

        except IntegrityError as error:
            await transaction.rollback()
            return (409, str(error))

        except Exception as error:  # pylint: disable=W0703
            await transaction.rollback()
            return (400, str(error))

    def unstructure(self, filter_fields=None, flat=True):
        """
        Converts a model instance to a dict.

        Only the pk field and the data fields are converted.
        datetime values are converted using the isoformat()
        method of datetime.datetime.
        """

        data = {}

        converters = {"datetime.datetime": lambda v: None if v is None else v.isoformat()}

        meta = Tortoise.describe_model(self.__class__)
        pk_field = meta["pk_field"]

        data[pk_field["name"]] = getattr(self, pk_field["name"])

        for field in meta["data_fields"]:
            name = field["name"]
            python_type = field["python_type"]

            if filter_fields is None or name in filter_fields:
                val = getattr(self, name)
                if val is not None:
                    if python_type in converters:
                        val = converters[python_type](val)
                    data[name] = val

        return data

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
