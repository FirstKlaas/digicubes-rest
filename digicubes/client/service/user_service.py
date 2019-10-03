"""
All user requests
"""
import logging
from typing import Optional, List

from digicubes.common.exceptions import (
    ConstraintViolation,
    ServerError,
    DoesNotExist,
    InsufficientRights,
    TokenExpired,
)

from digicubes.common.entities import RightEntity

from digicubes.configuration import Route

from .abstract_service import AbstractService
from ..proxy import UserProxy, RoleProxy

UserList = List[UserProxy]
XFieldList = Optional[List[str]]

logger = logging.getLogger(__name__)


class UserService(AbstractService):
    """
    All user calls
    """

    def all(
        self,
        token,
        fields: XFieldList = None,
        offset: Optional[int] = None,
        count: Optional[int] = None,
    ) -> UserList:
        """
        Gets all users.

        Returns a list of UserProxies. ``X-Filter-Fields`` is supported.
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.users)
        params = {}
        if offset:
            params["offset"] = offset

        if count:
            params["count"] = count

        result = self.requests.get(url, headers=headers, params=params)

        if result.status_code == 404:
            return []

        if result.status_code == 401:
            raise ValueError("Not authenticated")

        if result.status_code != 200:
            raise ServerError("Got an server error")

        data = result.json()
        user_data = data.get("result", None)
        if user_data is None:
            raise ServerError("No content provided.")

        return [UserProxy.structure(user) for user in user_data]

    def get_my_rights(self, token, fields: XFieldList = None):
        "Get my rights"
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.me_rights)
        result = self.requests.get(url, headers=headers)
        logger.debug("Requested rights. Status is %s", result.status_code)
        if result.status_code == 200:
            data = result.json()
            return [RightEntity.by_name(right) for right in data]

        raise TokenExpired("Could not read user rights. Token expired.")

    def get_my_roles(self, token, fields: XFieldList = None):
        "Get my roles"
        headers = self.create_default_header(token=token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.me_roles)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 200:
            data = result.json()
            return [RoleProxy.structure(role) for role in data]

        raise TokenExpired("Could not read user roles. Token expired.")

    def me(self, token, fields: XFieldList = None) -> Optional[UserProxy]:
        """
        Get a single user
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.me)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 401:
            raise TokenExpired("Could not read user details. Token expired.")

        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return UserProxy.structure(result.json())

        return None

    def get(self, token, user_id: int, fields: XFieldList = None) -> Optional[UserProxy]:
        """
        Get a single user
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.user, user_id=user_id)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 401:
            raise TokenExpired("Could not read user details. Token expired.")

        if result.status_code == 404:
            return None

        if result.status_code == 200:
            return UserProxy.structure(result.json())

        return None

    def set_password(
        self, token, user_id: int, new_password: str = None, old_password: str = None
    ) -> None:
        """
        Sets the password fo a user. If the current user has root rights, the old_password
        is not needed.
        """
        headers = self.create_default_header(token)
        data = {"password": new_password}
        url = self.url_for(Route.password, user_id=user_id)
        result = self.requests.post(url, headers=headers, data=data)

        if result.status_code == 400:
            raise DoesNotExist(f"No such user with id {user_id}")

        if result.status_code == 401:
            raise InsufficientRights("Not allowed")

        if result.status_code == 500:
            raise ServerError(result.text)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

    def delete(self, token, user_id: int) -> Optional[UserProxy]:
        """
        Deletes a user from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.user, user_id=user_id)
        result = self.requests.delete(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(f"User with user id {user_id} not found.")

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

        return UserProxy.structure(result.json())

    def delete_all(self, token) -> None:
        """
        Delete all users from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.users)
        result = self.requests.delete(url, headers=headers)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

    def create(self, token: str, user: UserProxy, fields: XFieldList = None) -> UserProxy:
        """
        Creates a new user
        """
        headers = self.create_default_header(token)
        data = user.unstructure()

        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(Route.users)
        result = self.requests.post(url, json=data, headers=headers)

        if result.status_code == 201:
            user_proxy: UserProxy = UserProxy.structure(result.json())
            if user.password is not None:
                self.set_password(user_proxy.id, user.password, token)

            return user_proxy

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_bulk(self, token, users: List[UserProxy]) -> None:
        """
        Create multiple users
        """
        headers = self.create_default_header(token)
        data = [user.unstructure() for user in users]
        url = self.url_for(Route.users)
        result = self.requests.post(url, json=data, headers=headers)
        if result.status_code == 201:
            return

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def update(self, token, user: UserProxy) -> UserProxy:
        """
        Update an existing user.
        If successfull, a new user proxy is returned with the latest version of the
        user data.
        """

        headers = self.create_default_header(token)
        url = self.url_for(Route.user, user_id=user.id)
        response = self.requests.post(url, json=user.unstructure(), headers=headers)

        if response.status_code == 404:
            raise DoesNotExist(response.text)

        if response.status_code == 500:
            raise ServerError(response.text)

        if response.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {response.status_code}")

        return UserProxy.unstructure(response.json())  # TODO CHeck other status_codes

    def get_roles(self, token, user: UserProxy) -> List[RoleProxy]:
        """
        Get all roles
        """
        # TODO Filter fields as parameter

        headers = self.create_default_header(token)
        url = self.url_for(Route.user_roles, user_id=user.id)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            raise DoesNotExist(result.text)

        if result.status_code != 200:
            raise ServerError(f"Wrong status. Expected 200. Got {result.status_code}")

        return [RoleProxy.structure(role) for role in result.json()]

    def add_role(self, token, user: UserProxy, role: RoleProxy) -> bool:
        """
        Adds a role to the user
        """
        headers = self.create_default_header(token)
        url = self.url_for(Route.user_role, user_id=user.id, role_id=role.id)
        result = self.requests.put(url, headers=headers)
        return result.status_code == 200
