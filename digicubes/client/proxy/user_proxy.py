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

    login: Optional[str] = None
    password: Optional[str] = None
    id: Optional[int] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    verified_at: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    last_login_at: Optional[str] = None
