"""
Usage:
    digicubes run
    digicubes --version

Options:
    --version     Show version.

"""
import logging
import os

from docopt import docopt

from . import DigiCubeServer

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


def evaluate_command():
    """
    Evaluates the commandline.
    """
    arguments = docopt(__doc__)
    print(arguments)
    if arguments.get("run", False):
        run()


def run():
    """
    Runs the server
    """
    from digicubes.web import create_app

    server = DigiCubeServer()

    if server.config.get("mount_web_app", False):
        mountpoint = server.config.get("web_app_mount_point", "/web")
        logger.info("Mounting web app. Mount point is: %s", mountpoint)
        server.mount(mountpoint, create_app())

    server.run()

def setup():
    """
    Creates an initial setup.
    """
    configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")
