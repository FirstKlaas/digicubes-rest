"""
A base class for all service endpoint.
"""
from typing import Any
from digicubes.configuration import Route

from digicubes.common.exceptions import (
    ConstraintViolation,
    ServerError,
    DoesNotExist,
    InsufficientRights,
)


class AbstractService:
    """
    This is an abstract base class for all
    digicube services.
    """

    X_FILTER_FIELDS = "X-Filter-Fields"

    __slots__ = ["client"]

    def __init__(self, client: Any) -> None:
        self.client = client

    @property
    def url(self) -> str:
        """The server url"""
        return self.client.url

    @property
    def requests(self):
        """
        Returns the requests object.
        """
        return self.client.requests

    @property
    def Right(self):
        """
        The right services
        """
        return self.client.right_service

    @property
    def User(self):
        """
        The user services
        """
        return self.client.user_service

    @property
    def Role(self):
        """
        The role services
        """
        return self.client.role_service

    def create_default_header(self, token):
        """
        Creates the default header for a standard
        call. Sets the bearer token as well as the
        accept header.
        """
        auth_value = f"Bearer {token}"
        return {"Authorization": auth_value, "Accept": "application/json"}

    def url_for(self, route: Route, **kwargs) -> str:
        # pylint: disable=C0111
        return self.client.url_for(route, **kwargs)

    def handle_common_exceptions(self, response):
        """
        A default handler for the most common exception.
        """
        if response.status_code == 401:
            return InsufficientRights()

        if response.status_code == 404:
            return DoesNotExist()

        if response.status_code == 409:
            return ConstraintViolation(response.text)

        if response.status_code == 500:
            return ServerError(response.text)

        return ServerError(f"Unknown error. [{response.status_code}] {response.text}")
