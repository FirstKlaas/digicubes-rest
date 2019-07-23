"""
First Testcase
"""
from datetime import datetime
import logging

from tortoise.exceptions import DoesNotExist, IntegrityError

from digicubes.storage import models as m
from . import BasicOrmTest

logging.root.setLevel(logging.FATAL)


class TestModified(BasicOrmTest):
    """
    Check modification dates of entities, after creating
    and changing
    """

    async def itest_check_defaults_for_user(self):
        """
        Testing dates exists after creation
        """
        u = await m.User.create(login="ratchet")
        self.assertIsNotNone(u.created_at)
        self.assertIsNotNone(u.modified_at)
        self.assertIsNotNone(u.id)
        self.assertIsInstance(u.id, int)
        self.assertIsInstance(u.created_at, datetime)
        self.assertIsInstance(u.modified_at, datetime)

    async def itest_user_not_exists(self):
        """
        Check if calling a non existing user throws
        an DoesNotExistException
        """
        with self.assertRaises(DoesNotExist):
            await m.User.get(id=88888)

    async def itest_unique_login(self):
        """
        Test unique constraint of User.login attribute
        """
        await m.User.all().delete()
        await m.User.create(login="clank")
        with self.assertRaises(IntegrityError):
            await m.User.create(login="clank")

    async def itest_modified_at(self):
        """
        See, if the modified_at gets updated correctly, when saving back
        a change.
        """
        u = await m.User.create(login="clank", email="clank@digicubes.org")
        self.assertTrue(u.modified_at >= u.created_at)
        m1 = u.modified_at
        u.email = "new_email"
        await u.save()
        self.assertTrue(u.modified_at > m1)
