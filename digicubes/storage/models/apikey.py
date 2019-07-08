from tortoise.models import Model
from tortoise import fields
from .support import BaseModel


class ApiKey(BaseModel):

    apikey = fields.CharField(24, unique=True, null=False)
    valid_from = fields.DateField()
    valid_until = fields.DateField()

    class Meta:
        table = "apikey"
