"""
A base class for all service endpoint.
"""
from typing import Any


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
