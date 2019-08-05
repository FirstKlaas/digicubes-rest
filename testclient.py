"""
Test client. Obsolet, when all test are written
"""
from datetime import time
import logging

from digicubes.client.proxy import UserProxy, SchoolProxy
from digicubes.client import DigiCubeClient
from digicubes.client.service.exceptions import ConstraintViolation

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
        ratchet = UserProxy(login="ratchet", password="clank")
        ratchet = User.create(ratchet)
    except ConstraintViolation:
        ratchet = User.get(2)

    User.set_password(ratchet.id, "moinsen")

    ratchet_client = DigiCubeClient(login="ratchet", password="moinsen")
