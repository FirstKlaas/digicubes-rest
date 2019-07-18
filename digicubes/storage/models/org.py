"""Model definition for the org module"""
import hashlib
import binascii
import os

from tortoise.fields import ManyToManyField

from .fields import Info, CharField, BooleanField, DatetimeField
from .support import BaseModel, NamedMixin

READONLY = Info(readable=True, writable=False)
WRITABLE = Info(readable=True, writable=True)
HIDDEN = Info(readable=False, writable=False)

class User(BaseModel):
    """User Model"""

    login = CharField(WRITABLE, 20, unique=True, description="The login name of the user.")    
    firstName = CharField(WRITABLE, 20, null=True)
    lastName = CharField(WRITABLE, 20, null=True)
    email = CharField(WRITABLE, 60, null=True)
    isActive = BooleanField(WRITABLE, null=False, default=False)
    isVerified = BooleanField(WRITABLE, null=False, default=False)
    password_hash = CharField(HIDDEN, 256, null=True)
    last_login_at = DatetimeField(READONLY, null=True)

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

    @password.setter
    def password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
        pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        pwdhash = (salt + pwdhash).decode("ascii")
        self.password_hash = pwdhash


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
