"""
All service calls for roles.
"""
from typing import Optional, List, Any

from .abstract_service import AbstractService
from .exceptions import ServerError, ConstraintViolation, DoesNotExist
from ..proxy import RoleProxy, RightProxy

RoleList = Optional[List[RoleProxy]]


class RoleService(AbstractService):
    """
    All role services
    """

    __slots__ = ["client"]

    def __init__(self, client: Any) -> None:
        super().__init__(client, "/roles/")

    def create(self, role: RoleProxy) -> RoleProxy:
        """
        Creates a new role
        """
        data = role.unstructure()
        result = self.requests.post(self.path, json=data)

        if result.status_code == 201:
            return RoleProxy.structure(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_bulk(self, roles: List[RoleProxy]) -> None:
        """
        Create multiple roles
        """
        data = [role.unstructure() for role in roles]
        result = self.requests.post(self.path, json=data)
        if result.status_code == 201:
            return

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def all(self) -> RoleList:
        """
        Returns all roles

        The result is a list of ``RoleProxy`` objects
        """
        result = self.requests.get(self.path)

        if result.status_code == 404:
            return []

        return [RoleProxy.structure(role) for role in result.json()]

    def get(self, role_id: int) -> Optional[RoleProxy]:
        """
        Get a single user.

        The requested user is specified by the ``id``.
        If the requested user was found, a ``UserProxy`` object
        will be returned. ``None`` otherwise.
        """
        result = self.requests.get(f"{self.path}{role_id}")

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code == 200:
            return RoleProxy.structure(result.json())

        return None

    def delete_all(self):
        """
        Removes all roles from the database.This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.
        """
        result = self.requests.delete(self.path)
        if result.status_code != 200:
            raise ServerError(result.text)

    def add_right(self, role: RoleProxy, right: RightProxy) -> bool:
        """
        Adds a right to this role.

        Because rights and roles have a many-to-many relation, this equivalent
        to adding a role to the right. Therefor the corresponding method from
        the right service is called.
        """
        return self.client.Right.add_role(right, role)

    def remove_right(self, role: RoleProxy, right: RightProxy) -> bool:
        """
        Removes a right from this role.

        Because rights and roles have a many-to-many relation, this equivalent
        to removing a role from the right. Therefor the corresponding method from
        the right service is called.
        """
        return self.client.Right.add_role(right, role)
