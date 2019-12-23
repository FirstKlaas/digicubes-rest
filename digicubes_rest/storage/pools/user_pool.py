# pylint: disable=C0111
import logging

from ..models import User
from .lru import LRU

logger = logging.getLogger(__name__)

# logger.setLevel(logging.DEBUG)


class UserPool:

    _cache = LRU(maxsize=512)

    @classmethod
    async def get_user(cls, user_id: int) -> User:
        """
        Returns a User for the given id
        """
        try:
            logger.debug("Requesting cache with id %d", user_id)
            return cls._cache[user_id]
        except KeyError:
            logger.debug("Didn't work requat user from database")
            user = await User.get(id=user_id)
            logger.debug("Returning user %s", user)
            cls._cache[user.id] = user
            return user
