"""
Test client. Obsolet, when all test are written
"""
import logging

from digicubes.client.proxy import UserProxy, SchoolProxy
from digicubes.client import DigiCubeClient
from digicubes.common.exceptions import ConstraintViolation
from digicubes.common.structures import BearerTokenData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    client = DigiCubeClient()
    cred: BearerTokenData = client.login(login="root", password="digicubes")
    print(cred)
    print('#'*80)

    token = cred.bearer_token
    user_id = cred.user_id

    logger.info("Successfully logged in on server %s", client.base_url)

    User = client.user_service
    Role = client.role_service
    Right = client.right_service
    School = client.school_service

    school = SchoolProxy(name="Realschule IX", description="My first school")
    School.create(token, school)
    for school in School.all(token):
        print(school)
