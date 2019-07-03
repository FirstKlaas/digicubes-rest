from tortoise import fields
from tortoise.models import Model

class DictConverter():

    __slots__ = []

    def as_dict(self, filtered_field_names:str=None):
        result = {}
        meta = getattr(self, '_meta', None)
        if meta is None:
            return result

        field_map = (meta.fields_map)
        for field_name in filtered_field_names:
            field = field_map.get(field_name,None)
            if field is not None:
                value = getattr(self, field_name)
                if isinstance(field, fields.DatetimeField) or isinstance(field, fields.DateField):
                    result[field_name] = value.isoformat()
                else:    
                    result[field_name] = field.to_db_value(value, self)
        return result

class BaseModel(DictConverter, Model):
    # pylint: disable=missing-docstring
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        abstract = True

class UUIDMixin():
    # pylint: disable=missing-docstring
    test = fields.UUIDField()

class NamedMixin():
    # pylint: disable=missing-docstring
    name = fields.TextField()

    @classmethod
    async def get_by_name(cls, name):
        return await cls.filter(name=name).first()
