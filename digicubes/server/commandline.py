"""
Usage:
    digicubes run
    digicubes setup
    digicubes --version

Options:
    --version     Show version.

"""
import logging
import os
import responder

from docopt import docopt

from digicubes.server.graphql.schema import schema

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
    elif arguments.get("setup", False):
        arguments.pop("run")
        try:
            setup(arguments)
        except KeyboardInterrupt:
            logger.info("\nSetup was canceled by user. No configuration file has been created.")


def run():
    """
    Runs the server
    """
    from digicubes.web import create_app

    server = DigiCubeServer()

    # Checks if the web frontend should be mounted
    # Defaults to no.
    if server.config.get("mount_web_app", False):
        mountpoint = server.config.get("web_app_mount_point", "/web")
        logger.info("Mounting web app. Mount point is: %s", mountpoint)
        server.mount(mountpoint, create_app())

    # Check, if we should setup the graphql route
    # Defaults to False.
    if server.config.get("mount_graphql", False):
        mountpoint = server.config.get("graphql_mount_point", "/graphql")        
        view = responder.ext.GraphQLView(api=server.api, schema=schema)
        server.api.add_route(mountpoint, view)

    server.run()


def setup(arguments):
    """
    Creates an initial setup.
    """

    def _read_port():
        port = None
        while port is None:
            port = input("Port to be used [3000]: ")
            if port == "":
                port = 3000
            else:
                try:
                    port = int(port)
                except ValueError:
                    logger.info("Please enter a number.")
        return port

    print(arguments)
    configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")
    if os.path.exists(configpath) and os.path.isdir(configpath):
        logger.info("Configuration directory exists. Good. Using '%s'.", configpath)
    else:
        logger.info("Configuration directory does not exist.")
        logger.info("Creating directory '%s'' for you.", configpath)
        os.makedirs(configpath)

    print(_read_port())
