"""
A base class for all service endpoint.
"""
from typing import Any


class AbstractService:
    """
    This is an abstract base class for all
    digicube services.
    """

    X_FILTER_FIELD = "X-Filter-Field"

    __slots__ = ["client", "base"]

    def __init__(self, client: Any, base: str) -> None:
        self.client = client
        self.base = base

    @property
    def url(self) -> str:
        """The server url"""
        return self.client.url

    @property
    def path(self) -> str:
        """The service base url"""
        return f"{self.url}{self.base}"

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
