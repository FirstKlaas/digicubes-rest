from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    # pylint: disable=missing-docstring

    @classmethod
    def from_dict(cls, data):
        model = cls()
        for field in cls.__public_fields__:
            if field in data: 
                setattr(model, field, data[field])
        return model

    def to_dict(self, filtered_field_names=None):
        result = {}
        meta = getattr(self, '_meta', None)
        if meta is None:
            return result

        public_fields = self.public_fields        

        field_map = (meta.fields_map)
        if filtered_field_names is None:
            filtered_field_names = public_fields
    
        for field_name in filtered_field_names:
            if field_name in public_fields:
                field = field_map.get(field_name,None)
                if field is not None:
                    value = getattr(self, field_name)
                    if isinstance(field, fields.DatetimeField) or isinstance(field, fields.DateField):
                        result[field_name] = value.isoformat()
                    elif isinstance(field, fields.ManyToManyField):    
                        print(f"igoring relation {field_name}")
                    elif isinstance(field, fields.ForeignKeyField):
                        print(f"ignoring foreign key field {field_name}")
                    else:
                        result[field_name] = value
                    
        return result

    @property
    def public_fields(self):
        calculated_fields = getattr(self.__class__, '__mro_public_fields__', None)
        if calculated_fields is not None:
            return calculated_fields
        
        result = []
        for cls in (self.__class__.__mro__):
            result.extend(getattr(cls, '__public_fields__', []))

        setattr(self.__class__, '__mro_public_fields__', result)
        return result

    __public_fields__ = [ 'id', 'created_at', 'modified_at']
    __mro_public_fields__ = None

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        abstract = True

class UUIDMixin():
    # pylint: disable=missing-docstring
    
    uuid = fields.UUIDField()

class NamedMixin():
    # pylint: disable=missing-docstring

    name = fields.TextField()

    @classmethod
    async def get_by_name(cls, name):
        return await cls.filter(name=name).first()
