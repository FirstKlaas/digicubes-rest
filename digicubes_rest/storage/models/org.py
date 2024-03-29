# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#
"""
Model definition for the org module
"""
import binascii
import hashlib
import logging
import os

from tortoise.fields import (BooleanField, CharField, DatetimeField,
                             ManyToManyField)
from werkzeug.security import check_password_hash, generate_password_hash

from .support import BaseModel, NamedMixin

# from digicubes_rest.server.ressource.util import has_right


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def hash_password(password: str) -> str:
    """
    Build a hashcode for this password.
    """
    if password is None:
        raise ValueError("No password provided to hash")

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    pwdhash = (salt + pwdhash).decode("ascii")
    return pwdhash


def verify_password(password_hash: str, password: str) -> None:
    """
    Generate a hashed password and compare it with the
    stored password hash.
    """
    if password is None:
        raise ValueError("No password provided to verify")

    if password_hash is None:
        raise ValueError("No password hash provided to verify")

    salt = password_hash[:64]
    stored_password = password_hash[64:]
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt.encode("ascii"), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return stored_password == pwdhash


class User(BaseModel):
    """User Model"""

    FIRST_NAME_LENGHT = 20
    LOGIN_LENGHT = 20
    LAST_NAME_LENGHT = 20
    EMAIL_LENGHT = 60

    login = CharField(LOGIN_LENGHT, unique=True, description="The login name of the user.")

    first_name = CharField(FIRST_NAME_LENGHT, null=True)
    last_name = CharField(LAST_NAME_LENGHT, null=True)
    email = CharField(EMAIL_LENGHT, null=True)
    is_active = BooleanField(null=True, default=False)
    is_verified = BooleanField(null=True, default=False)
    verified_at = DatetimeField(null=True)
    password_hash = CharField(256, null=True)
    last_login_at = DatetimeField(null=True)

    roles = ManyToManyField("model.Role", related_name="users", through="user_roles")

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "user"
        ordering = ["login", "last_name", "first_name"]

    class PydanticMeta:
        include = (
            "id",
            "login",
            "last_login_at",
            "first_name",
            "last_name",
            "verified_at",
            "created_at",
        )

    def __str__(self):
        return "User"

    @property
    def password(self):
        """
        Reading the password is forbidden.
        """
        raise EnvironmentError()

    @property
    def is_password_set(self):
        """
        Checks, if the password has been set.
        """
        return self.password_hash is not None

    @password.setter
    def password(self, password):
        """Hash a password for storing."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> None:
        """
        Generate a hashed password and compere it with the
        stored password hash.
        """
        if not self.is_password_set:
            return False
        return check_password_hash(self.password_hash, password)


class Role(NamedMixin, BaseModel):
    """
    The role model.

    Users can have multiple roles. Roles can have multiple rights. This is how user rights
    are modeled.
    """

    DESCRIPTION_LENGTH = 60
    HOME_ROUTE_LENGTH = 40

    description = CharField(DESCRIPTION_LENGTH, null=True, default="")
    home_route = CharField(HOME_ROUTE_LENGTH, null=True)

    # pylint: disable=missing-docstring
    rights = ManyToManyField("model.Right", related_name="roles", through="roles_rights")

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "role"

    def __str__(self):
        return f"{self.name} [id={self.id}]"


class Right(NamedMixin, BaseModel):
    """
    The right model.

    Rights simply have a name. Rights belong to one or many roles.
    """

    DESCRIPTION_LENGTH = 60

    description = CharField(DESCRIPTION_LENGTH, null=True, default="")

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "right"

    def __str__(self):
        return f"{self.name} [id={self.id}]"
