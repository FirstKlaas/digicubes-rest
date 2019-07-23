"""
The data representation of a right.
"""
from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class RightProxy(AbstractProxy):
    """
    Represents a right.

    The ``id`` attribute is the primary key
    and cannot be changed.

    The ``name`` attribute is mandatory. All
    other fields are optional.
    """

    name: str
    id: Optional[int] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
