"""
All service calls for roles.
"""
from typing import Optional, List

from digicubes.configuration import Route
from .abstract_service import AbstractService
from ..proxy import RoleProxy, RightProxy

RoleList = Optional[List[RoleProxy]]


class RoleService(AbstractService):
    """
    All role services
    """

    def create(self, token, role: RoleProxy) -> RoleProxy:
        """
        Creates a new role.

        The parameter role contains the data for the new role. Not every attribute
        has to carry values. But at least all mandatory attributes must. If any
        model constraint is violated by the provided data, a ``ConstraintViolation``
        error will be raised. THe message of the error should give you a good indication
        what is wrong with the data.

        :param RoleProxy role: The role you want to create. Be shure, that at least all
            non null attributes have meaningful values. Attributes like ``id``, ``created_at``
            and ``modified_at`` will be ignored.

        """
        headers = self.create_default_header(token)
        data = role.unstructure()
        url = self.url_for(Route.roles)
        result = self.requests.post(url, json=data, headers=headers)

        if result.status_code == 201:
            return RoleProxy.structure(result.json())

        raise self.handle_common_exceptions(result)

    def create_bulk(self, token, roles: List[RoleProxy]) -> None:
        """
        Create multiple roles
        """
        headers = self.create_default_header(token)
        data = [role.unstructure() for role in roles]
        url = self.url_for(Route.roles)
        result = self.requests.post(url, json=data, headers=headers)
        if result.status_code == 201:
            return

        raise self.handle_common_exceptions(result)

    def all(self, token) -> RoleList:
        """
        Returns all roles

        The result is a list of ``RoleProxy`` objects
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.roles)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            return [RoleProxy.structure(role) for role in result.json()]

        raise self.handle_common_exceptions(result)

    def get(self, token, role_id: int) -> Optional[RoleProxy]:
        """
        Get a single user.

        The requested user is specified by the ``id``.
        If the requested user was found, a ``UserProxy`` object
        will be returned. ``None`` otherwise.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.role, role_id=role_id)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            return RoleProxy.structure(result.json())

        raise self.handle_common_exceptions(result)

    def delete_all(self, token):
        """
        Removes all roles from the database.This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.roles)
        result = self.requests.delete(url, headers=headers)
        if result.status_code != 200:
            raise self.handle_common_exceptions(result)

    def add_right(self, token, role: RoleProxy, right: RightProxy) -> bool:
        """
        Adds a right to this role.

        """
        if role is None or role.id is None:
            raise ValueError(f"Invalid role {role}")

        if right is None or right.id is None:
            raise ValueError(f"Invalid right {right}")

        self.Right.add_role(token, right, role)

    def remove_right(self, token, role: RoleProxy, right: RightProxy) -> bool:
        """
        Removes a right from this role.

        Because rights and roles have a many-to-many relation, this equivalent
        to removing a role from the right. Therefor the corresponding method from
        the right service is called.
        """
        raise NotImplementedError()

    def get_rights(self, token, role: RoleProxy) -> List[RightProxy]:
        """
        Get all rights assiciated with this role.

        """

        headers = self.create_default_header(token)
        url = self.url_for(Route.role_rights, role_id=role.id)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            return [RightProxy.structure(right) for right in result.json()]

        return self.handle_common_exceptions(result)
