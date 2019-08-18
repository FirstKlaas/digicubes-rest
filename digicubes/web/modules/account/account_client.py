"""
Flask Extension to add a digicube client
to a Flask Server
"""
import logging

from digicubes.client import DigiCubeClient
from digicubes.common.exceptions import DigiCubeError

logger = logging.getLogger(__name__)


class AccountClient:
    """
    """

    def __init__(self, **kwargs):
        logger.debug("Creating new client with args: %s", kwargs)
        self._client = DigiCubeClient(**kwargs)
        # self._client.login('root', 'digicubes')

    @property
    def token(self):
        return self._client.token

    @token.setter
    def token(self, value):
        logger.debug("Storing client token")
        self._client.token = value

    @property
    def is_authorized(self):
        return self.token is not None

    def logout(self):
        if self.token is None:
            return False

        self.token = None
        return True

    def login(self, login: str, password: str) -> str:
        try:
            self._client.login(login, password)
        except DigiCubeError:
            pass
        return self.token

    @property
    def user(self):
        """user servives"""
        return self._client.user_service

    @property
    def role(self):
        """role servives"""
        return self._client.role_service

    @property
    def version(self):
        return "0.0.0"