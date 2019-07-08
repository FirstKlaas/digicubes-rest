"""Model definition for the org module"""
import hashlib, binascii, os
 
from tortoise.fields import (
    IntField, TextField, 
    CharField, DatetimeField, 
    ManyToManyField, ForeignKeyField, 
    UUIDField, IntField, BooleanField)

from tortoise.models import Model
from .support import BaseModel, NamedMixin

class User(BaseModel):
    # pylint: disable=missing-docstring
    __updatable_fields__ = ['firstName','lastName','email','isActive', 'isVerified'] 
    __public_fields__ = __updatable_fields__ + ['login'] 

    login = CharField(20, unique=True, description="The login name of the user.")
    firstName = CharField(20, null=True)
    lastName = CharField(20, null=True)
    email = CharField(60, null=True)
    isActive = BooleanField(null=False, default=False)
    isVerified = BooleanField(null=False, default=False)
    password_hash = CharField(256,null=True)
    roles = ManyToManyField('model.Role', related_name="users", through='user_roles')
    
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
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        pwdhash = (salt + pwdhash).decode('ascii')
        print(pwdhash)
        self.password_hash = pwdhash

class Role(NamedMixin, BaseModel):
    # pylint: disable=missing-docstring
    rights = ManyToManyField('model.Right', related_name="roles", through='roles_rights')

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "role"

    def __str__(self):
        return f"{self.name} [id={self.id}]"

class Right(NamedMixin, BaseModel):
    # pylint: disable=missing-docstring

    class Meta:
        # pylint: disable=too-few-public-methods
        # pylint: disable=missing-docstring
        table = "right"

    def __str__(self):
        return f"{self.name} [id={self.id}]"
