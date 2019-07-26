"""Testcase"""
from digicubes.client.proxy import RoleProxy

from . import BasicServerTest


class TestRequest(BasicServerTest):
    """
    Test the roles endpoint.
    """

    def test_bulk_roles(self):
        """
        test for bulk creation
        """

        # Let's create a bunch of roles
        roles = [RoleProxy(name=f"role_{i}") for i in range(20)]
        self.Role.create_bulk(roles)

        # Now request all roles.
        roles = self.Role.all()
        # We should get 20 roles back
        self.assertEqual(len(roles), 20)

        # Now delete all roles
        self.Role.delete_all()

        # Now request all roles.
        roles = self.Role.all()
        # We should get 0 roles back
        self.assertEqual(len(roles), 0)
