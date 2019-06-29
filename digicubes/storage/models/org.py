"""Model definition for the org module"""

from tortoise.fields import (IntField, TextField, DatetimeField)
from tortoise.models import Model


class User(Model):
    # pylint: disable=missing-docstring
    id = IntField(pk=True)
    name = TextField()
    created_at = DatetimeField(null=True)

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "user"

    def __str__(self):
        return f"{self.name} [{self.id}]"
