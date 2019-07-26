"""Testcase"""
from digicubes.server import ressource as endpoint
from digicubes.client.proxy import UserProxy, RoleProxy, RightProxy

from . import BasicServerTest


class TestRequest(BasicServerTest):
    """
    Test the users endpoint.
    """

    def test_users(self):
        """
        Requests test for users.
        """
        url = self.api.url_for(endpoint.UsersRessource)
        response = self.api.requests.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

        # Create a user
        response = self.api.requests.post(url, data={"login": "ratchet"})

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("id", data.keys())
        self.assertIsNotNone(data["id"])
        self.assertIsInstance(data["id"], int)

        # Create the same user for a second time which
        # leads to a constraint violation as the login
        # must be unique
        response = self.api.requests.post(url, data={"login": "ratchet"})
        self.assertEqual(response.status_code, 409)
        url = self.api.url_for(endpoint.UserRessource, user_id=1)

    def test_client_create_new_user(self):
        """
        Create a new user via the digicubes client.
        """
        user = self.User.create(
            UserProxy(login="ratchet", first_name="ratchet"), fields=["modified_at", "created_at"]
        )
        # After creation of a user, the to fields created_at and
        # modified_at should have decent values.
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.modified_at)

        # Create a single admin role ...
        adminRole = self.Role.create(RoleProxy(name="Admin"))
        # ... and add it to the user
        self.User.add_role(user, adminRole)

        roles = self.User.get_roles(user)
        self.assertEqual(len(roles), 1)

        # Create ne new right
        delete_user_right = self.Right.create(RightProxy(name="DELETE_USER"))
        # and add it to the role
        self.Role.add_right(adminRole, delete_user_right)

        # We added only one right to this role.
        # So let's get the right sfor this role.
        # There should be only one right and the
        # right should have the name DELETE_USER
        rights = self.Role.get_rights(adminRole)
        self.assertEqual(len(rights), 1)
        self.assertEqual(rights[0].name, "DELETE_USER")

        # Now check the reverse relation.
        roles = self.Right.get_roles(rights[0])
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0].name, "Admin")

        # TODO: Role.get_rights

    def test_bulk_users(self):
        """
        Test for bulk creation of users
        """
        # Let's create som users
        users = [UserProxy(login=f"login_{i}") for i in range(20)]
        self.User.create_bulk(users)
        # Now get all users
        users = self.User.all()
        # we should get 20 users
        self.assertEqual(len(users), 20)
