"""
Model definition for the org module
"""
import hashlib
import os
import logging

import binascii

from tortoise.fields import ManyToManyField, CharField, BooleanField, DatetimeField
from werkzeug.security import check_password_hash, generate_password_hash

# from digicubes.server.ressource.util import has_right

from .support import BaseModel, NamedMixin

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

    login = CharField(20, unique=True, description="The login name of the user.")
    first_name = CharField(20, null=True)
    last_name = CharField(20, null=True)
    email = CharField(60, null=True)
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

    def __str__(self):
        return f"{self.login} [id={self.id}]"

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


#    def has_right(self, rights):
#        """
#        Checks if the user has atleast one of the
#        provided rights
#        """
#        return has_right(self, rights)


class Role(NamedMixin, BaseModel):
    """
    The role model.

    Users can have multiple roles. Roles can have multiple rights. This is how user rights
    are modeled.
    """

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

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "right"

    def __str__(self):
        return f"{self.name} [id={self.id}]"
