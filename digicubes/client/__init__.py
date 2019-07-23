"""
    Client for the DigiCubeServer
"""

import json

import requests as reqmod

from .proxy import UserProxy
from .service import UserService, RoleService, RightService, SchoolService


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
    ]

    def __init__(self, url: str, requests=None) -> None:
        self.url = url
        self.user_service = UserService(self)
        self.role_service = RoleService(self)
        self.right_service = RightService(self)
        self.school_service = SchoolService(self)
        if requests is not None:
            self.requests = requests
            self.url = ""
        else:
            self.requests = reqmod
