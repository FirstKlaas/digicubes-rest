"""Model definition for the org module"""

from tortoise.fields import (
    IntField, TextField, 
    CharField, DatetimeField, 
    ManyToManyField, ForeignKeyField, 
    UUIDField, IntField)

from tortoise.models import Model


class BaseModel(Model):
    # pylint: disable=missing-docstring
    id = IntField(pk=True)
    created_at = DatetimeField(null=True, auto_now_add=True)
    modified_at = DatetimeField(null=True, auto_now=True)

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        abstract = True

class UUIDMixin():
    # pylint: disable=missing-docstring
    test = UUIDField()

class NamedMixin():
    # pylint: disable=missing-docstring
    name = TextField()

    @classmethod
    async def get_by_name(cls, name):
        return await cls.filter(name=name).first()

class User(BaseModel):
    # pylint: disable=missing-docstring
    id = UUIDField(pk=True)
    login = CharField(20, unique=True)
    firstName = CharField(20, null=True)
    lastName = CharField(20, null=True)
    email = CharField(60, null=True)
    isActive = IntField(null=True)
    roles = ManyToManyField('model.Role', related_name="users", through='user_roles')

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "user"

    def __str__(self):
        return f"{self.login} [id={self.id}]"


class Role(NamedMixin, BaseModel):
    # pylint: disable=missing-docstring
    rights = ManyToManyField('model.Right', related_name="roles", through='roles_rights')

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "role"

    def __str__(self):
        return f"{self.name} [id={self.id}]"

class Right(NamedMixin, BaseModel):
    # pylint: disable=missing-docstring

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "right"

    def __str__(self):
        return f"{self.name} [id={self.id}]"
