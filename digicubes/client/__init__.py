"""
    Client for the DigiCubeServer
"""

import json
import logging

import cattr
import requests

from digicubes.common.exceptions import DoesNotExist
from digicubes.common import structures as st
from digicubes.common.exceptions import TokenExpired, ServerError
from digicubes.configuration import url_for, Route

from .proxy import UserProxy
from .service import UserService, RoleService, RightService, SchoolService

logger = logging.getLogger(__name__)


class DigiCubeClient:
    """
    The main client class, to communicate with the digicube server
    """

    @staticmethod
    def init(server):
        client =  DigiCubeClient()
        client.requests = server.api.requests
        return client

    __slots__ = [
        "protocol",
        "hostname",
        "port",
        "user_service",
        "role_service",
        "right_service",
        "school_service",
        "requests",
        "__token",
    ]

    def __init__(
            self,
            protocol: str = "http",
            hostname: str = "localhost",
            port: int = 3000,
        ) -> None:
        self.protocol = protocol
        self.hostname = hostname
        self.port = port
        self.user_service = UserService(self)
        self.role_service = RoleService(self)
        self.right_service = RightService(self)
        self.school_service = SchoolService(self)

        self.requests = requests
        self.__token = None


    def login(self, login, password):
        logger.info("Login with account %s to get bearer token.", login)
        data = {"login": login, "password": password}
        headers = {"accept": "application/json"}
        # TODO: Use url_for
        response = self.requests.post(self.url_for(Route.login), data=data, headers=headers)

        if response.status_code == 404:
            raise DoesNotExist(f"User with login {login} does not exist.")

        if response.status_code != 200:
            raise ServerError(response.text)

        data = st.BearerTokenData.structure(response.json())
        self.token = data.bearer_token
        logger.info("Bearer token is %s.", self.token)

    def url_for(self, route: Route, **kwargs):
        """
        Get the formatted url for a given route.
        """
        return self.base_url + route.value.format(**kwargs)

    @property
    def base_url(self):
        """
        Returns the base url for the server.
        """
        if self.hostname is None:
            return ""

        return f"{self.protocol}://{self.hostname}:{self.port}"

    @property
    def token(self):
        """
        The bearer token for this client.
        """
        #if self.__token is None:
        #    raise TokenExpired("No token set. Normally this means, that the token has expired.")
        return self.__token

    @token.setter
    def token(self, value):
        self.__token = value

    def create_default_header(self):
        """
        Creates the default header for a standard
        call. Sets the bearer token as well as the
        accept header.
        """
        auth_value = f"Bearer {self.token}"
        return {"Authorization": auth_value, "Accept": "application/json"}

    def refresh_token(self):
        """
        Requesting a new bearer token.
        """
        logger.info("Refreshing bearer token")
        url = self.url_for(Route.new_token)
        headers = self.create_default_header()
        response = self.requests.post(url, headers=headers)
        if response.status_code == 200:
            data = st.BearerTokenData.structure(response.json())
            self.token = data.bearer_token
            logger.debug("Token refreshed. New token is: %s", self.token)
        elif response.status_code == 401:
            self.token = None
            raise TokenExpired("Your auth token has expired.")
        else:
            self.token = None
            raise ServerError("A server error occurred.")
