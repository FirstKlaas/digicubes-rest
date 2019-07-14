"""Model definition for the org module"""
import hashlib
import binascii
import os

from tortoise.fields import CharField, ManyToManyField, BooleanField

from .support import BaseModel, NamedMixin


class User(BaseModel):
    """User Model"""

    # pylint: disable=missing-docstring
    __updatable_fields__ = ["firstName", "lastName", "email", "isActive", "isVerified"]
    __public_fields__ = __updatable_fields__ + ["login", "id"]

    login = CharField(20, unique=True, description="The login name of the user.")
    """Login"""
    firstName = CharField(20, null=True)
    lastName = CharField(20, null=True)
    email = CharField(60, null=True)
    isActive = BooleanField(null=False, default=False)
    isVerified = BooleanField(null=False, default=False)
    password_hash = CharField(256, null=True)
    roles = ManyToManyField("model.Role", related_name="users", through="user_roles")

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "user"

    def __str__(self):
        return f"{self.login} [id={self.id}]"

    @property
    def password(self):
        raise EnvironmentError()

    @password.setter
    def password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
        pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        pwdhash = (salt + pwdhash).decode("ascii")
        print(pwdhash)
        self.password_hash = pwdhash


class Role(NamedMixin, BaseModel):
    """
    The role model.

    Users can have multiple roles. Roles can have multiple rights. This is how user rights
    are modeled.
    """

    __updatable_fields__ = ["name"]
    __public_fields__ = __updatable_fields__

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

    __updatable_fields__ = ["name"]
    __public_fields__ = __updatable_fields__

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "right"

    def __str__(self):
        return f"{self.name} [id={self.id}]"
