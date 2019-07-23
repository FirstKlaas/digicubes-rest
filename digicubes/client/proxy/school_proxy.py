"""
The data representation of a school.
"""
from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class SchoolProxy(AbstractProxy):
    """
    Represents a school.
    """

    name: str
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
