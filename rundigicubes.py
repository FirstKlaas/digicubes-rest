import logging

from digicubes.server import DigiCubeServer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    server = DigiCubeServer()
    server.run()
