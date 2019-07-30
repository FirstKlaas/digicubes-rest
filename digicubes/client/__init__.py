"""
    Client for the DigiCubeServer
"""

import json
import logging

import cattr
import requests as reqmod

from digicubes.common import structures as st
from .proxy import UserProxy
from .service import UserService, RoleService, RightService, SchoolService
from .service.exceptions import DoesNotExist

logger = logging.getLogger(__name__)


class DigiCubeClient:
    """
    The main client class, to communicate with the digicube server
    """

    # pylint: disable=too-few-public-methods

    __slots__ = [
        "url",
        "user_service",
        "role_service",
        "right_service",
        "school_service",
        "requests",
        "token",
    ]

    def __init__(self, url: str, requests=None, login=None, password=None) -> None:
        self.url = url
        self.user_service = UserService(self)
        self.role_service = RoleService(self)
        self.right_service = RightService(self)
        self.school_service = SchoolService(self)

        # What request should be used.
        # Standard requests library or a provided
        # library.
        if requests is not None:
            self.requests = requests
            self.url = ""
        else:
            self.requests = reqmod

        # Now login
        if login is not None:
            logger.info("Login with account %s to get bearer token.", login)
            data = {"login": login, "password": password}
            headers = {"accept": "application/json"}
            # TODO: Use url_for
            response = self.requests.post("/login/", data=data, headers=headers)
            if response.status_code == 404:
                raise DoesNotExist(f"User with login {login} does not exist.")
            data = st.BearerTokenData.structure(response.json())
            self.token = data.bearer_token
            logger.info("Bearer token is %s.", self.token)
        else:
            raise ValueError("No credential provided")
