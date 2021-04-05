from typing import List

from pydantic import BaseModel, Field, PositiveInt

from .abstract_base import ResponseModel
from .org_model import UserModel


class PaginationModel(BaseModel):
    count: PositiveInt = 0
    limit: PositiveInt = 0
    offset: PositiveInt = 0


class LinksModel(BaseModel):
    anchor_self: str = Field("", alias="self")


class PagedUserModel(ResponseModel):
    pagination: PaginationModel = PaginationModel()
    links: LinksModel = LinksModel()
    result: List[UserModel] = []
