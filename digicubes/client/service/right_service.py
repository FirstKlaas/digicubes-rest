"""
All serice calls for rights
"""
from typing import Any, List, Optional

from digicubes.configuration import url_for, Route
from .abstract_service import AbstractService
from .exceptions import ServerError, DoesNotExist, ConstraintViolation
from ..proxy import RightProxy, RoleProxy

RightList = List[RightProxy]


class RightService(AbstractService):
    """
    The rights service
    """

    def __init__(self, client: Any) -> None:
        super().__init__(client)

    def create(self, right: RightProxy) -> RightProxy:
        """
        Creates a new right
        """
        data = right.unstructure()
        url = url_for(Route.rights)
        result = self.requests.post(url, json=data)

        if result.status_code == 201:
            return RightProxy.structure(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def all(self) -> RightList:
        """
        Returns all rigths.
        The result is a list of ``RightProxy`` objects.
        """
        url = url_for(Route.rights)
        result = self.requests.get(url)

        if result.status_code == 404:
            return []

        return [RightProxy.structure(right) for right in result.json()]

    def get(self, right_id: int) -> Optional[RightProxy]:
        """
        Get a single right by id
        """
        url = url_for(Route.right, right_id=right_id)
        result = self.requests.get(url)
        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return RightProxy.structure(result.json())

        return None

    def delete_all(self):
        """
        Delete all digicube rights. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.

        """
        url = url_for(Route.rights)
        result = self.requests.delete(url)
        if result.status_code != 200:
            raise ServerError(result.text)

    def get_roles(self, right: RightProxy) -> List[RoleProxy]:
        # TODO: Use Filter fields
        """
        Get all roles associated with this right
        """
        url = url_for(Route.right_roles, right_id=right.id)
        result = self.requests.get(url)

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code == 200:
            return [RoleProxy.structure(role) for role in result.json()]

        raise ServerError(result.text)

    def add_role(self, right: RightProxy, role: RoleProxy) -> bool:
        """
        Add a role to this right. The role and the right must exist.
        If not, a DoesNotExist error is raised.
        """
        url = url_for(Route.right_role, right_id=right.id, role_id=role.id)
        result = self.requests.put(url)
        if result.status_code == 404:
            raise DoesNotExist(result.text)

        return result.status_code == 200

    def remove_role(self, right: RightProxy, role: RoleProxy) -> bool:
        """
        Removes a role from this right. Both, the role and the right must exist.
        If not, a ``DoesNotExist`` exception is thrown.
        """
        url = url_for(Route.right_role, right_id=right.id, role_id=role.id)
        response = self.requests.delete(url)

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False

    def clear_roles(self, right: RightProxy) -> bool:
        """
        Clears all roles from the right. After a succesful call no
        role is associated with this right. The right must exist.
        At least the id of the right has to be set.

        :param RightProxy right: The right, where the roles should be cleared.

        :return bool: True, if the operation was successful, False else.
        """
        url = url_for(Route.right_roles, right_id=right.id)
        response = self.requests.delete(url)

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False
