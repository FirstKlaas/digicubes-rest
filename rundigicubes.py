import logging

from digicubes.server.commandline import run

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    run()
