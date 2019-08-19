"""Testcase"""
from digicubes.client.proxy import RoleProxy

from . import BasicServerTest


class TestRequest(BasicServerTest):
    """Test roles endpoint"""

    def test_bulk_roles(self):
        """Role bulk creation"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        # See, how many roles we have at the
        # start of the test.
        number_of_roles = len(self.Role.all(token))
        number_of_dummy_roles = 20
        # Let's create a bunch of roles
        roles = [RoleProxy(name=f"role_{i}") for i in range(number_of_dummy_roles)]
        self.Role.create_bulk(token, roles)

        # Now request all roles.
        roles = self.Role.all(token)
        # We should get 20 roles back
        self.assertEqual(len(roles), number_of_dummy_roles + number_of_roles)
