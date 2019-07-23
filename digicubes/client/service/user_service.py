"""
All user requests
"""
from typing import Any, Optional, List

from .abstract_service import AbstractService
from .exceptions import ConstraintViolation, ServerError, DoesNotExist
from ..proxy import UserProxy, RoleProxy

UserList = List[UserProxy]
XFieldList = Optional[List[str]]


class UserService(AbstractService):
    """
    All user calls
    """

    __slots__ = ["client"]

    def __init__(self, client: Any) -> None:
        super().__init__(client, "/users/")

    def all(self, fields: XFieldList = None) -> UserList:
        """
        Gets all users.

        Returns a list of UserProxies. ``X-Filter-Field`` is supported.
        """
        headers = {}
        if fields is not None:
            headers[self.X_FILTER_FIELD] = ",".join(fields)

        result = self.requests.get(self.path, headers=headers)

        if result.status_code == 404:
            return []

        return [UserProxy.structure(user) for user in result.json()]

    def get(self, user_id: int, fields: XFieldList = None) -> Optional[UserProxy]:
        """
        Get a single user
        """
        headers = {}
        if fields is not None:
            headers[self.X_FILTER_FIELD] = ",".join(fields)

        result = self.requests.get(f"{self.path}{user_id}", headers=headers)

        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return UserProxy.structure(result.json())

        return None

    def delete(self, user_id: int) -> Optional[UserProxy]:
        """
        Deletes a user from the database
        """
        result = self.requests.delete(f"{self.path}{user_id}")
        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return UserProxy.structure(result.json())

        return None

    def delete_all(self) -> None:
        """
        Delete all users from the database
        """
        result = self.requests.delete(self.path)
        if result.status_code != 200:
            raise ServerError(result.text)

    def create(self, user: UserProxy) -> UserProxy:
        """
        Creates a new user
        """
        data = user.unstructure()
        result = self.requests.post(self.path, json=data)

        if result.status_code == 201:
            return UserProxy.structure(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_bulk(self, users: List[UserProxy]) -> None:
        """
        Create multiple users
        """
        data = [user.unstructure() for user in users]
        result = self.requests.post(self.path, json=data)
        if result.status_code == 201:
            return

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def update(self, user: UserProxy) -> UserProxy:
        """
        Update an existing user.
        If successfull, a new user proxy is returned with the latest version of the
        user data.
        """
        response = self.requests.post(f"{self.path}{user.id}", json=user.unstructure())

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        if response.status_code == 500:
            raise ServerError(response.text)

        return UserProxy.unstructure(response.json())  # TODO CHeck other status_codes

    def get_roles(self, user: UserProxy) -> List[RoleProxy]:
        """
        Get all roles

        """
        url = f"{self.path}{user.id}/roles/"
        result = self.requests.get(url)
        if result.status_code == 200:
            return [RoleProxy.structure(role) for role in result.json()]

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def add_role(self, user: UserProxy, role: RoleProxy) -> bool:
        """
        Adds a role to the user
        """
        url = f"{self.path}{user.id}/roles/{role.id}"
        result = self.requests.put(url)
        return result.status_code == 200
