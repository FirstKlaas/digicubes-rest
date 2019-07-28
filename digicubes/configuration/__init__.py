"""
Configuration module

Supporting functions and classes for better configuration.

"""
from enum import Enum


class Route(Enum):
    """
    All available url patterns
    """

    login = "/login/"
    users = "/users/"
    user = "/users/{user_id}"
    user_roles = "/users/{user_id}/roles/"
    user_role = "/users/{user_id}/roles/{role_id}"
    user_rights = "/users/{user_id}/rights/"

    roles = "/roles/"
    role = "/roles/{role_id}"
    role_rights = "/roles/{role_id}/rights/"
    role_right = "/roles/{role_id}/rights/{right_id}"

    rights = "/rights/"
    right = "/rights/{right_id}"
    right_roles = "/rights/{right_id}/roles/"
    right_role = "/rights/{right_id}/roles/{role_id}"

    schools = "/schools/"
    school = "/school/{school_id}"


def url_for(route: Route, **kwargs) -> str:
    """
    Get the formatted url for a given route.
    """
    return route.value.format(**kwargs)
