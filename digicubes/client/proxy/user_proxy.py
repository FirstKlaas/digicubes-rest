"""
The data representation of a user.
"""
from typing import Optional
import attr
from .abstract_proxy import AbstractProxy


@attr.s(auto_attribs=True)
class UserProxy(AbstractProxy):
    """
    Represents a user.

    :param int id: The ``id`` attribute is the primary key and
        cannot be changed.

    :param str login: The ``login`` attribute is mandatory.
        The login must be unique. All other fields are optional.

    :param str email: A valid email for the user
    """

    login: str
    id: Optional[int] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    isActive: Optional[bool] = None
    isVerified: Optional[bool] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    last_login_at: Optional[str] = None
    etag: Optional[str] = None
