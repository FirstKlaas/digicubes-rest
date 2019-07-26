"""
API Key Model
"""
from .support import BaseModel

from .fields import DateField, CharField, Info


class ApiKey(BaseModel):
    # pylint: disable=R0903
    """
    Api Key Model

    To use the api, you need a valid API-KEY
    """

    apikey = CharField(Info(), 24, unique=True, null=False)
    valid_from = DateField(Info(), null=True)
    valid_until = DateField(Info(), null=True)

    class Meta:
        # pylint: disable=C0111, R0903
        table = "apikey"
