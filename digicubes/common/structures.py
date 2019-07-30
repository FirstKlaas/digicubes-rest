from typing import Optional

import attr
import cattr


class BaseData:
    @classmethod
    def structure(cls, data):
        return cattr.structure(data, cls)

    def unstructure(self):
        return cattr.unstructure(self)


@attr.s(auto_attribs=True)
class LoginData(BaseData):
    login: str
    password: str


@attr.s(auto_attribs=True)
class BearerTokenData(BaseData):
    bearer_token: str
    user_id: int


@attr.s(auto_attribs=True)
class PasswordData(BaseData):
    user_id: int
    user_login: str
    password_hash: Optional[str] = None
