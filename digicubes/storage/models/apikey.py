"""
API Key Model
"""
from tortoise import fields
from .support import BaseModel


class ApiKey(BaseModel):
    # pylint: disable=R0903
    """
    Api Key Model

    To use the api, you need a valid API-KEY
    """

    apikey = fields.CharField(24, unique=True, null=False)
    valid_from = fields.DateField()
    valid_until = fields.DateField()

    class Meta:
        # pylint: disable=C0111, R0903
        table = "apikey"
