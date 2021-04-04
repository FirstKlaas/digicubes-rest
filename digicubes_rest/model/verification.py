from pydantic import BaseModel

from .org_model import UserModel


class VerificationInfo(BaseModel):
    user: UserModel
    token: str
