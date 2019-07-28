"""
First Testcase
"""
from digicubes.server import ressource
from . import BasicServerTest


class TestMethodNotAllowed(BasicServerTest):
    """
    Check all Method not allowed calls
    """

    def test_users_put(self):
        """
        PUT /users/
        """
        url = self.api.url_for(ressource.UsersRessource)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_post(self):
        """
        POST /users/(int: user_id)
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRessource, user_id=user.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_post(self):
        """
        POST /users/(int: user_id)/roles/
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_put(self):
        """
        PUT /users/(int: user_id)/roles/
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_role_post(self):
        """
        POST /users/(int: user_id)/roles/(int: role_id)
        """
        user = self.create_ratchet()
        role = self.create_test_role("TEST_ROLE")
        url = self.api.url_for(ressource.UserRoleRessource, user_id=user.id, role_id=role.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_roles_put(self):
        """
        PUT /roles/
        """
        url = self.api.url_for(ressource.RolesRessource)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_post(self):
        """
        POST /roles/42
        """
        role = self.create_test_role("TEST_ROLE")
        url = self.api.url_for(ressource.RoleRessource, role_id=role.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_post(self):
        """
        POST /roles/42/rights/
        """
        role = self.create_test_role("TEST_ROLE")
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_put(self):
        """
        PUT /roles/42/rights/
        """
        role = self.create_test_role("TEST_ROLE")
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_right_post(self):
        """
        POST /roles/42/right/17
        """
        role = self.create_test_role("TEST_ROLE")
        right = self.create_right("TEST_RIGHT")
        url = self.api.url_for(ressource.RoleRightRessource, role_id=role.id, right_id=right.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_rights_put(self):
        """
        PUT /rights/
        """
        url = self.api.url_for(ressource.RightsRessource)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_post(self):
        """
        POST /rights/1
        """
        right = self.create_right("TEST_RIGHT")
        url = self.api.url_for(ressource.RightRessource, right_id=right.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_roles_put(self):
        """
        PUT /rights/1/roles/
        """
        right = self.create_right("TEST_RIGHT")
        url = self.api.url_for(ressource.RightRolesRessource, right_id=right.id)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_roles_post(self):
        """
        POST /rights/1/roles
        """
        right = self.create_right("TEST_RIGHT")
        url = self.api.url_for(ressource.RightRolesRessource, right_id=right.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_role_post(self):
        """
        POST /rights/1/roles/32
        """
        right = self.create_right("TEST_RIGHT")
        role = self.create_test_role("TEST_ROLE")
        url = self.api.url_for(ressource.RightRoleRessource, right_id=right.id, role_id=role.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_schools_put(self):
        """
        PUT /schools/
        """
        url = self.api.url_for(ressource.SchoolsRessource)
        headers = self.create_default_headers()
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_school_post(self):
        """
        POST /school/1
        """
        school = self.create_school("TEST_SCHOOL")

        url = self.api.url_for(ressource.SchoolRessource, school_id=school.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_rights(self):
        """
        User Rights. ONly get is allowed
        """
        user = self.create_ratchet()
        url = self.api.url_for(ressource.UserRightsRessource, user_id=user.id)
        headers = self.create_default_headers()
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)
        result = self.api.requests.delete(url, headers=headers)
        self.assertEqual(result.status_code, 405)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)
