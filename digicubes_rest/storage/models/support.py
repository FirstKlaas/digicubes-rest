"""
Helper module with some use functions as well as the base model.
"""

import logging
from datetime import date, datetime

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
        try:
            meta = Tortoise.describe_model(cls)
            obj = cls()
            for field in meta["data_fields"]:
                name = field["name"]

                if name in data:
                    python_type = field["python_type"]
                    value = data[name]
                    if python_type == "datetime.date":
                        value = date.fromisoformat(data[name])
                    elif python_type == "datetime.datetime":
                        value = datetime.fromisoformat(data[name])
                    elif python_type == "bool":
                        value = bool(data[name])
                    setattr(obj, name, value)
        except Exception as error:  # pylint: disable=broad-except
            logger.fatal("Cannot structure %s.", cls, exc_info=error)
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
        async with transactions.in_transaction():
            try:
                if isinstance(data, dict):
                    logger.info("Creating ressource for class %s.", cls)
                    res = cls.structure(data)

                    await res.save()
                    return (201, res.unstructure(filter_fields))

                if isinstance(data, list):
                    logger.info("Creating multiple ressources in bulk mode.")
                    res = [cls.structure(item) for item in data]
                    await cls.bulk_create(res)
                    return (201, None)

                return (500, f"Unsupported data type {type(data)}")

            except IntegrityError as error:
                logger.exception("Could not create instance of class %s", cls)
                return (409, str(error))

            except Exception as error:  # pylint: disable=W0703
                logger.exception("Could not create instance of class %s", cls)
                logger.fatal("Could not create course. Reason:", exc_info=True)
                return (400, str(error))

    def unstructure(self, filter_fields=None, flat=True, exclude_fields=None):
        """
        Converts a model instance to a dict.

        Only the pk field and the data fields are converted.
        datetime values are converted using the isoformat()
        method of datetime.datetime.

        """

        def datetime_convert(val):
            """
            Converts a datetime object to string.
            If value is None, returns None and
            if val is a string, returns the string
            without any checking.
            """
            if val is None:
                return None

            val_type = type(val)
            if val_type is str:
                return val

            if val_type is datetime:
                return val.isoformat()

            raise ValueError(f"Value ({val}) has unsupported type {type(val)}")

        data = {}

        converters = {
            "datetime.datetime": datetime_convert,
            "datetime.date": lambda v: None if v is None else v.isoformat(),
        }

        # TODO: Does it make sens to cache this information?
        meta = Tortoise.describe_model(self.__class__)

        pk_field = meta["pk_field"]

        if hasattr(self, pk_field["name"]):
            data[pk_field["name"]] = getattr(self, pk_field["name"])

        def is_included(name):
            return filter_fields is None or name in filter_fields

        def is_excluded(name):
            return exclude_fields is not None and name in exclude_fields

        for field in meta["data_fields"]:
            name = field["name"]
            python_type = field["python_type"]
            if is_included(name) and not is_excluded(name) and hasattr(self, name):
                val = getattr(self, name)
                if val is not None:
                    if python_type in converters:
                        val = converters[python_type](val)
                    data[name] = val

        return data

    def update(self, data):
        """
        Updates this instance with new values.

        All values are taken as they are. Only for fields
        of type datetime.date and datetime.datetime are
        converted from str to date or datetime. The string
        has to be iso formatted.
        """
        # TODO: Does it make sense to cache this information?
        meta = Tortoise.describe_model(self.__class__)
        data_fields = {f["name"]: f for f in meta["data_fields"]}

        for key, value in data.items():
            if value is not None:
                # See, if we have to to any conversions
                # For date abd datetime values, we expect
                # the incoming value to be an iso string
                # TODO: What if we already get an date or datetime object?
                field = data_fields.get(key, None)
                if field:
                    python_type = field["python_type"]
                    if python_type == "datetime.date":
                        assert isinstance(
                            value, str
                        ), f"Expected {key} to be str type. Got {type(value)}"
                        value = date.fromisoformat(value)
                    elif python_type == "datetime.datetime":
                        assert isinstance(
                            value, str
                        ), f"Expected {key} to be str type. Got {type(value)}"
                        value = datetime.fromisoformat(value)

                    setattr(self, key, value)

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
        return await cls.get_or_None(name=name)
