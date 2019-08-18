"""
Flask Extension to add a digicube client
to a Flask Server
"""
import logging

from digicubes.client import DigiCubeClient, UserService
from digicubes.common.exceptions import DigiCubeError, NotAuthenticated

logger = logging.getLogger(__name__)


class AccountClient:
    """
    """
    def __init__(self, **kwargs):
        logger.debug("Creating new client with args: %s", kwargs)
        self._client: DigiCubeClient = DigiCubeClient(**kwargs)

    @property
    def token(self):
        return self._client.token

    def token_for(self, login, password):
        return self._client.generate_token_for(login, password)

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
        return self._client.login(login, password)

    @property
    def roles(self):
        """
        Get the roles, that the current
        User is associated to.
        """
        if not self.is_authorized:
            raise NotAuthenticated("User not authorized")

        return self.user.get_my_roles()

    @property
    def rights(self):
        """
        Get the roles, that the current
        User is associated to.
        """
        if not self.is_authorized:
            raise NotAuthenticated("User not authorized")

        return self.user.get_my_rights()

    @property
    def user(self) -> UserService:
        """user servives"""
        return self._client.user_service

    @property
    def role(self):
        """role services"""
        return self._client.role_service

    @property
    def version(self):
        return "0.0.0"
