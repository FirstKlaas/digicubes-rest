"""Testcase"""
import logging

from digicubes.common import structures as st
from digicubes.server import ressource as endpoint

# from digicubes.client.proxy import UserProxy, RoleProxy, RightProxy

from . import BasicServerTest

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class TestRequest(BasicServerTest):
    """
    Creates a new user and tries to loog in.
    """

    def test_new_user(self):
        """Create new user and login"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(endpoint.UsersRessource)
        headers = self.create_default_headers(token)

        # Create a ratchet
        login_data = st.LoginData(login="ratchet", password="clank")
        data = login_data.unstructure()
        response = self.api.requests.post(url, data=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        user_data = response.json()
        logger.debug("User Data: %s", user_data)
        self.assertIsNotNone(user_data.get("id", None))

        logger.debug("Setting password")
        url = self.api.url_for(endpoint.PasswordRessource, user_id=user_data["id"])
        response = self.api.requests.post(url, data=data, headers=headers)
        self.assertEqual(response.status_code, 200, response.text)
        password_info = response.json()
        self.assertIsNotNone(password_info.get("user_id", None))
        self.assertEqual(password_info["user_id"], user_data["id"])

        # Now try to login
        url = self.api.url_for(endpoint.LoginRessource)
        response = self.api.requests.post(url, data=data, headers=headers)

        # Because the the user is not verified and not active
        # authentification shoud fail
        self.assertEqual(response.status_code, 401)

        # Now update the user, so he is able to login
        url = self.api.url_for(endpoint.UserRessource, user_id=user_data["id"])
        update_data = {"is_active": True, "is_verified": True}
        response = self.api.requests.put(url, data=update_data, headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

        # Retry login. Now it should work.
        url = self.api.url_for(endpoint.LoginRessource)
        response = self.api.requests.post(url, data=data)
        self.assertEqual(response.status_code, 200, response.text)
        rt = st.BearerTokenData.structure(response.json())

        # Now try to get all users with the new ratchet account
        # It should fail, because ratchet has not sufficient rights.
        ratchet_headers = {"Authorization": f"Bearer {rt.bearer_token}"}
        url = self.api.url_for(endpoint.UsersRessource)
        response = self.api.requests.get(url, headers=ratchet_headers)
        self.assertEqual(response.status_code, 401)
