# pylint: disable=C0111
from enum import Enum, unique


@unique
class Right(Enum):
    """Standard Rights"""

    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    DELETE_ALL_USER = "delete_all_user"

    @classmethod
    def values(cls):
        """
        Returns an array of the names
        """
        return [right.value for right in cls]
