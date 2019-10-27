"""
The data representation of a school.
"""
from datetime import date, datetime
import json

from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class SchoolProxy(AbstractProxy):
    """
    Represents a school.
    """

    id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    description: Optional[str] = None

@attr.s(auto_attribs=True)
class CourseProxy(AbstractProxy):
    """
    Represents a school.
    """

    id: Optional[int] = None
    name: Optional[str] = None
    is_private: Optional[bool] = None
    school_id: Optional[int] = None
    created_by_id: Optional[int] = None
    description: Optional[str] = None
    from_date: Optional[date] = None

    def to_json_dict(self):

        data = self.unstructure()
        print(data)
        data["from_date"] = self.from_date.isoformat()
        print(data)
        return data
