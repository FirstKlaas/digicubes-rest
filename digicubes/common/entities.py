# pylint: disable=C0111
from enum import Enum


class RoleEntity(Enum):
    """
    Standard roles
    """

    ROOT = {"name": "root"}
    ADMIN = {"name": "admin"}

    @property
    def name(self):
        return dict(self.value)["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class RightEntity(Enum):
    """
    Standard Rights
    """

    CREATE_USER = {"name": "create_user", "roles": [RoleEntity.ROOT]}
    READ_USER = {"name": "read_user", "roles": [RoleEntity.ROOT]}
    UPDATE_USER = {"name": "update_user", "roles": [RoleEntity.ROOT]}
    DELETE_USER = {"name": "delete_user", "roles": [RoleEntity.ROOT]}
    DELETE_ALL_USER = {"name": "delete_all_user", "roles": [RoleEntity.ROOT]}

    @property
    def name(self):
        return dict(self.value)["name"]

    @property
    def roles(self):
        return dict(self.value)["roles"]

    @property
    def role_names(self):
        return [role.value["name"] for role in self.roles]

    @classmethod
    def for_role(cls, role: RoleEntity):
        """
        Returns a list of right names associated
        with given role.
        """
        return [right.value["name"] for right in cls if role in right.value["roles"]]

    @classmethod
    def values(cls):
        """
        Returns an array of the names
        """
        return [right.value["name"] for right in cls]

    def __str__(self):
        return dict(self.value)["name"]

    def __repr__(self):
        return dict(self.value)["name"]
