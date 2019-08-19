"""Testcase"""
from digicubes.server import ressource as endpoint
from digicubes.client.proxy import UserProxy, RoleProxy, RightProxy

from . import BasicServerTest


class TestRequest(BasicServerTest):
    """Test the users endpoint."""

    def test_users(self):
        """Requests test for users."""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(endpoint.UsersRessource)
        headers = self.create_default_headers(token)
        response = self.api.requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

        # Create a user
        response = self.api.requests.post(url, data={"login": "ratchet"}, headers=headers)

        self.assertEqual(response.status_code, 201, response.text)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("id", data.keys())
        self.assertIsNotNone(data["id"])
        self.assertIsInstance(data["id"], int)

        # Create the same user for a second time which
        # leads to a constraint violation as the login
        # must be unique
        response = self.api.requests.post(url, data={"login": "ratchet"}, headers=headers)
        self.assertEqual(response.status_code, 409)

    def test_client_create_new_user(self):
        """
        Create a new user via the digicubes client.
        """
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        proxy = UserProxy(login="ratchet", first_name="ratchet")
        fields = ["modified_at", "created_at"]
        user = self.User.create(token, proxy, fields=fields)
        # After creation of a user, the to fields created_at and
        # modified_at should have decent values.
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.modified_at)

        count_roles = len(self.User.get_roles(token, user))

        # Create a single admin role ...
        testRole = self.Role.create(token, RoleProxy(name="TEST_ROLE"))
        # ... and add it to the user
        self.User.add_role(token, user, testRole)

        roles = self.User.get_roles(token, user)
        self.assertEqual(len(roles), count_roles + 1)

        # Create a new right
        test_right = self.Right.create(token, RightProxy(name="TEST_RIGHT"))
        # and add it to the role
        self.Role.add_right(token, testRole, test_right)

        # We added only one right to this role.
        # So let's get the right sfor this role.
        # There should be only one right and the
        # right should have the name DELETE_USER
        rights = self.Role.get_rights(token, testRole)
        self.assertEqual(len(rights), 1)
        self.assertEqual(rights[0].name, "TEST_RIGHT")

        # Now check the reverse relation.
        roles = self.Right.get_roles(token, rights[0])
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0].name, "TEST_ROLE")

        # TODO: Role.get_rights
