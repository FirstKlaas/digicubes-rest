import logging

from digicubes.server import DigiCubeServer
from digicubes.web import DigiWeb

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    server = DigiCubeServer()
    server.add_extension(DigiWeb())
    server.run()
