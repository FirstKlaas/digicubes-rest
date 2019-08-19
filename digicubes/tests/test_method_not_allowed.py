"""
First Testcase
"""
from digicubes.server import ressource
from . import BasicServerTest


class TestMethodNotAllowed(BasicServerTest):
    """Check all Method not allowed calls"""

    def test_users_put(self):
        """PUT /users/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(ressource.UsersRessource)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_post(self):
        """POST /users/(int: user_id)"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        user = self.create_ratchet(token)
        url = self.api.url_for(ressource.UserRessource, user_id=user.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_post(self):
        """POST /users/(int: user_id)/roles/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        user = self.create_ratchet(token)
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_roles_put(self):
        """PUT /users/(int: user_id)/roles/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        user = self.create_ratchet(token)
        url = self.api.url_for(ressource.UserRolesRessource, user_id=user.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_role_post(self):
        """POST /users/(int: user_id)/roles/(int: role_id)"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        user = self.create_ratchet(token)
        role = self.create_test_role(token, "TEST_ROLE")
        url = self.api.url_for(ressource.UserRoleRessource, user_id=user.id, role_id=role.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_roles_put(self):
        """PUT /roles/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(ressource.RolesRessource)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_post(self):
        """POST /roles/42"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        role = self.create_test_role(token, "TEST_ROLE")
        url = self.api.url_for(ressource.RoleRessource, role_id=role.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_post(self):
        """POST /roles/42/rights/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        role = self.create_test_role(token, "TEST_ROLE")
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_rights_put(self):
        """PUT /roles/42/rights/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        role = self.create_test_role(token, "TEST_ROLE")
        url = self.api.url_for(ressource.RoleRightsRessource, role_id=role.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_role_right_post(self):
        """POST /roles/42/right/17"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        role = self.create_test_role(token, "TEST_ROLE")
        right = self.create_right(token, "TEST_RIGHT")
        url = self.api.url_for(ressource.RoleRightRessource, role_id=role.id, right_id=right.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_rights_put(self):
        """PUT /rights/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(ressource.RightsRessource)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_post(self):
        """POST /rights/1"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        right = self.create_right(token, "TEST_RIGHT")
        url = self.api.url_for(ressource.RightRessource, right_id=right.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_roles_put(self):
        """PUT /rights/1/roles/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        right = self.create_right(token, "TEST_RIGHT")
        url = self.api.url_for(ressource.RightRolesRessource, right_id=right.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_roles_post(self):
        """POST /rights/1/roles"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        right = self.create_right(token, "TEST_RIGHT")
        url = self.api.url_for(ressource.RightRolesRessource, right_id=right.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_right_role_post(self):
        """POST /rights/1/roles/32"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        right = self.create_right(token, "TEST_RIGHT")
        role = self.create_test_role(token, "TEST_ROLE")
        url = self.api.url_for(ressource.RightRoleRessource, right_id=right.id, role_id=role.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_schools_put(self):
        """PUT /schools/"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(ressource.SchoolsRessource)
        headers = self.create_default_headers(token)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_school_post(self):
        """POST /school/1"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        school = self.create_school(token, "TEST_SCHOOL")

        url = self.api.url_for(ressource.SchoolRessource, school_id=school.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)

    def test_user_rights(self):
        """User Rights. ONlY get is allowed"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        user = self.create_ratchet(token)
        url = self.api.url_for(ressource.UserRightsRessource, user_id=user.id)
        headers = self.create_default_headers(token)
        result = self.api.requests.post(url, headers=headers)
        self.assertEqual(result.status_code, 405)
        result = self.api.requests.delete(url, headers=headers)
        self.assertEqual(result.status_code, 405)
        result = self.api.requests.put(url, headers=headers)
        self.assertEqual(result.status_code, 405)
