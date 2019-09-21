"""
Test client. Obsolet, when all test are written
"""
import logging

from digicubes.client.proxy import UserProxy, SchoolProxy
from digicubes.client import DigiCubeClient
from digicubes.common.exceptions import ConstraintViolation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    client = DigiCubeClient()
    cred = client.login(login="root", password="digicubes")
    print(cred)
    print('#'*80)
    c2 = client.login(login="flori", password="suppenhuhn")
    print(c2)
    print('#'*80)
    
    
    logger.info("Successfully logged in on server %s", client.base_url)

    User = client.user_service
    Role = client.role_service
    Right = client.right_service
    School = client.school_service

    users = User.all(cred.bearer_token, count=200)
    for user in users:
        print(f"{user.login:<15} id={user.id}") 

    User.set_password(cred.bearer_token, 3, "suppenhuhn")
    
    print('#'*80)
    print(User.me(c2.bearer_token))