"""
All serice calls for rights
"""
from typing import List, Optional

from digicubes.common.exceptions import ConstraintViolation, ServerError, DoesNotExist
from digicubes.configuration import Route
from .abstract_service import AbstractService
from ..proxy import RightProxy, RoleProxy

RightList = List[RightProxy]


class RightService(AbstractService):
    """
    The rights service
    """

    def create(self, token, right: RightProxy) -> RightProxy:
        """
        Creates a new right
        """
        headers = self.create_default_header(token)
        data = right.unstructure()
        url = self.url_for(Route.rights)
        result = self.requests.post(url, json=data, headers=headers)

        if result.status_code == 201:
            return RightProxy.structure(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def all(self, token) -> RightList:
        """
        Returns all rigths.
        The result is a list of ``RightProxy`` objects.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.rights)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            return []

        return [RightProxy.structure(right) for right in result.json()]

    def get(self, token, right_id: int) -> Optional[RightProxy]:
        """
        Get a single right by id
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.right, right_id=right_id)
        result = self.requests.get(url, headers=headers)
        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return RightProxy.structure(result.json())

        return None

    def delete_all(self, token):
        """
        Delete all digicube rights. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.

        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.rights)
        result = self.requests.delete(url, headers=headers)
        if result.status_code != 200:
            raise ServerError(result.text)

    def get_roles(self, token, right: RightProxy) -> List[RoleProxy]:
        # TODO: Use Filter fields
        """
        Get all roles associated with this right
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.right_roles, right_id=right.id)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code == 200:
            return [RoleProxy.structure(role) for role in result.json()]

        raise ServerError(result.text)

    def add_role(self, token, right: RightProxy, role: RoleProxy) -> bool:
        """
        Add a role to this right. The role and the right must exist.
        If not, a DoesNotExist error is raised.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.right_role, right_id=right.id, role_id=role.id)
        result = self.requests.put(url, headers=headers)
        if result.status_code == 404:
            raise DoesNotExist(result.text)

        return result.status_code == 200

    def remove_role(self, token, right: RightProxy, role: RoleProxy) -> bool:
        """
        Removes a role from this right. Both, the role and the right must exist.
        If not, a ``DoesNotExist`` exception is thrown.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.right_role, right_id=right.id, role_id=role.id)
        response = self.requests.delete(url, headers=headers)

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False

    def clear_roles(self, token, right: RightProxy) -> bool:
        """
        Clears all roles from the right. After a succesful call no
        role is associated with this right. The right must exist.
        At least the id of the right has to be set.

        :param RightProxy right: The right, where the roles should be cleared.

        :return bool: True, if the operation was successful, False else.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.right_roles, right_id=right.id)
        response = self.requests.delete(url, headers=headers)

        if response.status_code == 200:
            return True

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        return False
