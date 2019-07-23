"""Testcase"""
from digicubes.server import ressource as endpoint

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
