"""
API Key Model
"""
from tortoise.fields import DateField, CharField

from .support import BaseModel


class ApiKey(BaseModel):
    # pylint: disable=R0903
    """
    Api Key Model

    To use the api, you need a valid API-KEY
    """

    apikey = CharField(24, unique=True, null=False)
    valid_from = DateField(null=True)
    valid_until = DateField(null=True)

    class Meta:
        # pylint: disable=C0111, R0903
        table = "apikey"
