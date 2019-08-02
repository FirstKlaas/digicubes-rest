# pylint: disable=C0111
# pylint: disable=C0111

from typing import Optional

import attr
import cattr


class BaseData:
    """
    Base class for data classes used as body content
    in requests.
    """

    @classmethod
    def structure(cls, data):
        # pylint: disable=C0111
        return cattr.structure(data, cls)

    def unstructure(self):
        # pylint: disable=C0111
        return cattr.unstructure(self)


@attr.s(auto_attribs=True)
class LoginData(BaseData):
    # pylint: disable=C0111
    login: str
    password: str


@attr.s(auto_attribs=True)
class BearerTokenData(BaseData):
    # pylint: disable=C0111
    bearer_token: str
    user_id: int


@attr.s(auto_attribs=True)
class PasswordData(BaseData):
    # pylint: disable=C0111
    user_id: int
    user_login: str
    password_hash: Optional[str] = None
