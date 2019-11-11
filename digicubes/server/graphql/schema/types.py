"""
Typedefinition of the graphene types, wich reflect the 
models from the ORM definition.
"""
import graphene


class UserType(graphene.ObjectType):
    """
    UserType wich reflects the orm User definition without
    the relations.
    """

    id = graphene.Int()
    login = graphene.String()
    firstName = graphene.String()
    lastName = graphene.String()
