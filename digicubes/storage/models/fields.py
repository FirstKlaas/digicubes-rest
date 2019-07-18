"""
My own fields
"""
from datetime import datetime
from typing import Callable, Any

import attr
from tortoise import fields

def base_converter(info, field, val):
    if val is None or isinstance(val, (int, str, float, )):
        return val

    if isinstance(val, datetime):
        return val.isoformat()

    raise ValueError(f"Unsupported  value type <{type(val)}>")

Converter = Callable[[Any, fields.Field, Any],Any]

@attr.s(auto_attribs=True)
class Info:
    """
    Info class. Used for storing meta information
    for fields.
    """

    readable: bool = True
    writable: bool = False
    attribute: bool = True

    convert: Converter = base_converter


class BooleanField(fields.BooleanField):
    """
    Adds an additional info attribute
    """
    __slots__ = ("info",)

    def __init__(self, info: Info, **kwargs) -> None:
        self.info = info
        super().__init__(**kwargs)

class CharField(fields.CharField):
    """
    Adds an additional info attribute
    """
    __slots__ = ("info",)

    def __init__(self, info: Info, max_length: int, **kwargs) -> None:
        self.info = info
        super().__init__(max_length, **kwargs)

class IntField(fields.IntField):
    """
    Adds an additional info attribute
    """
    __slots__ = ("info",)

    def __init__(self, info: Info, **kwargs) -> None:
        self.info = info
        super().__init__(**kwargs)

class DatetimeField(fields.DatetimeField):
    """
    Adds an additional info attribute
    """
    __slots__ = ("info",)

    def __init__(self, info: Info, **kwargs) -> None:
        self.info = info
        super().__init__(**kwargs)

class DateField(fields.DateField):
    """
    Adds an additional info attribute
    """
    __slots__ = ("info",)

    def __init__(self, info: Info, **kwargs) -> None:
        self.info = info
        super().__init__(**kwargs)
