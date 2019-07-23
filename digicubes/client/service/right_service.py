"""
All serice calls for rights
"""
from typing import Any, List, Optional

from .abstract_service import AbstractService
from .exceptions import ServerError, DoesNotExist
from ..proxy import RightProxy, RoleProxy

RightList = List[RightProxy]


class RightService(AbstractService):
    """
    The rights service
    """

    def __init__(self, client: Any) -> None:
        super().__init__(client, "/rights/")

    def all(self) -> RightList:
        """
        Returns all rigths.
        The result is a list of ``RightProxy`` objects.
        """
        result = self.requests.get(self.path)

        if result.status_code == 404:
            return []

        return [RightProxy.structure(right) for right in result.json()]

    def get(self, right_id: int) -> Optional[RightProxy]:
        """
        Get a single right by id
        """
        result = self.requests.get(f"{self.path}{right_id}")
        if result.status_code == 404:
            return None

        if result.status_code == 200:
            print(result.headers)
            return RightProxy.structure(result.json())

        return None

    def delete_all(self):
        """
        Delete all digicube rights. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.

        """
        result = self.requests.delete(self.path)
        if result.status_code != 200:
            raise ServerError(result.text)

    def add_role(self, right: RightProxy, role: RoleProxy) -> bool:
        """
        Add a role to this right. The role and the right must exist.
        If not, a DoesNotExist error is raised.
        """
        result = self.requests.put(f"{self.path}{right.id}/roles/{role.id}")
        print(result.status_code)
        if result.status_code == 404:
            raise DoesNotExist(result.text)

        return result.status_code == 200

    def remove_role(self, right: RightProxy, role: RoleProxy) -> bool:
        """
        Removes a role from this right. Both, the role and the right must exist.
        If not, a ``DoesNotExist`` exception is thrown.
        """
        response = self.requests.delete(f"{self.path}{right.id}/roles/{role.id}")

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
        response = self.requests.delete(f"{self.path}{right.id}/roles/")

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False
