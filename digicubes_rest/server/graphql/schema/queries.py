import graphene

from digicubes_rest.storage.models.org import User
from .types import UserType


class Query(graphene.ObjectType):

    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())

    async def resolve_all_users(self, info):
        users = await User.all()
        return users

    async def resolve_user(self, info, uid):
        user = await User.get(id=uid)
        return user
