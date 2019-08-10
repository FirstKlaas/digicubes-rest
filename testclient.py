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
    client = DigiCubeClient(login="root", password="digicubes")
    logger.info("Successfully logged in on server %s", client.base_url)

    User = client.user_service
    Role = client.role_service
    Right = client.right_service
    School = client.school_service

    try:
        ratchet = UserProxy(login="lena", password="ratchet", is_verified=True, is_active=True)
        ratchet = User.create(ratchet)
    except ConstraintViolation:
        ratchet = User.get(2)

    for user in User.all():
        print(f"{user.id} : {user.login}")
