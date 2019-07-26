"""
First Testcase
"""
import logging

from digicubes.server import ressource
from . import BasicServerTest

logging.root.setLevel(logging.FATAL)


class TestMethodNotAllowed(BasicServerTest):
    """
    Check all Method not allowed calls
    """

    def test_users_put(self):
        """
        PUT /users/
        """
        url = self.api.url_for(ressource.UsersRessource)
        result = self.api.requests.put(url)
        self.assertEqual(result.status_code, 405)

    def test_user_post(self):
        """
        POST /users/(int: user_id)
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRessource, user_id=user.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_post(self):
        """
        POST /users/(int: user_id)/roles
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_put(self):
        """
        PUT /users/(int: user_id)/roles
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        result = self.api.requests.put(url)
        self.assertEqual(result.status_code, 405)

    def test_user_role_post(self):
        """
        POST /users/(int: user_id)/roles/(int: role_id)
        """
        user = self.create_ratchet()
        role = self.create_admin_role()
        url = self.api.url_for(ressource.UserRoleRessource, user_id=user.id, role_id=role.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)

    def test_roles_put(self):
        """
        PUT /roles/
        """
        url = self.api.url_for(ressource.RolesRessource)
        result = self.api.requests.put(url)
        self.assertEqual(result.status_code, 405)

    def test_role_post(self):
        """
        POST /roles/42
        """
        role = self.create_admin_role()
        url = self.api.url_for(ressource.RoleRessource, role_id=role.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_post(self):
        """
        POST /roles/42/rights
        """
        role = self.create_admin_role()
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_put(self):
        """
        PUT /roles/42/rights
        """
        role = self.create_admin_role()
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        result = self.api.requests.put(url)
        self.assertEqual(result.status_code, 405)

    def test_role_right_post(self):
        """
        POST /roles/42/right/17
        """
        role = self.create_admin_role()
        right = self.create_right("TEST_RIGHT")
        url = self.api.url_for(ressource.RoleRightRessource, role_id=role.id, right_id=right.id)
        result = self.api.requests.post(url)
        self.assertEqual(result.status_code, 405)
