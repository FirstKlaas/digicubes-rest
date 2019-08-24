# pylint: disable=C0111
import logging

# from datetime import timedelta
from time import sleep
from typing import Dict

from digicubes.common import structures as st
from digicubes.server import ressource as endpoint

from digicubes.server.ressource.util import create_bearer_token


from . import BasicServerTest

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class TestRenewToken(BasicServerTest):
    # pylint: disable=C0111

    def get_bearer_token(self, url: str, headers: Dict[str, str]) -> st.BearerTokenData:
        response = self.api.requests.post(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        logger.debug("Logging response data: %s", data)
        return st.BearerTokenData.structure(data)

    def test_renew_token(self):
        """Renew the token for root"""
        # Run test with root priviledges
        token = self.root_token
        self.assertIsNotNone(token)

        url = self.api.url_for(endpoint.RenewTokenRessource)
        headers = self.create_default_headers(token)
        scheme, old_token = headers["Authorization"].split(" ")
        logger.debug("Old token: %s", old_token)
        self.assertEqual(scheme, "Bearer")
        self.assertIsNotNone(old_token)
        sleep(1)
        rt = self.get_bearer_token(url, headers)
        self.assertIsNotNone(rt.bearer_token)
        logger.debug(rt)
        logger.debug(self.create_authorization_header(token))

        # self.assertNotEqual(old_token, rt.bearer_token)

    def test_token_generation(self):
        """Two tokens are different"""
        t1 = create_bearer_token(1, self.api.secret_key)
        sleep(1)
        t2 = create_bearer_token(1, self.api.secret_key)
        self.assertIsNotNone(t1)
        self.assertIsNotNone(t2)
        self.assertNotEqual(t1, t2)
