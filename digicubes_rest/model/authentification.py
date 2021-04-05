from typing import Optional

from pydantic import PositiveInt

from .abstract_base import ResponseModel


class BearerTokenData(ResponseModel):
    bearer_token: str
    user_id: PositiveInt
    lifetime: int  # Lifetime (max age) of this token
    expires_at: str  # expiration date as iso formatted string


class LoginData(ResponseModel):
    # pylint: disable=C0111
    login: str
    password: str


class PasswordData(ResponseModel):
    # pylint: disable=C0111
    user_id: PositiveInt
    user_login: str
    password_hash: Optional[str] = None


__all__ = [BearerTokenData, LoginData, PasswordData]
