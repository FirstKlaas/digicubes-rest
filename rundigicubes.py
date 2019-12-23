"""
Simple helper to run the server.
"""
import logging

from digicubes_rest.server.commandline import run

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    run()
