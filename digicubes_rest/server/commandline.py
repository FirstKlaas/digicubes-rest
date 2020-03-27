"""
Usage:
    digicubes run
    digicubes setup
    digicubes cfg [--out-dir=<path>] [--mode=<name>]
    digicubes --version

Options:
    --version           Show version.
    --out-dir=<path>    Path to store the configuration file. Defaults to
                        the current directory. If you provide a value, the
                        path must exist. Path will not be created.
    --mode=<name>       You can create multiple configuration files for
                        different modes, like production or development.
                        If no mode is provided it defaults to 'configuration',
                        which will create a file called 'configuration.yaml'. 

"""
import logging
import os
import responder

from docopt import docopt

from digicubes_rest.server.graphql.schema import schema

from . import DigiCubeServer

logger = logging.getLogger(__name__)


def evaluate_command():
    """
    Evaluates the commandline.
    """
    arguments = docopt(__doc__)
    print(arguments)
    if arguments.get("run", False):
        run()
    elif arguments.get("cfg", False):
        cfg(arguments)
    elif arguments.get("setup", False):
        try:
            setup(arguments)
        except KeyboardInterrupt:
            logger.info("\nSetup was canceled by user. No configuration file has been created.")


def cfg(arguments):
    from pathlib import Path

    base_path = Path(__file__).parent
    in_file = (base_path / "../configuration/apiserver.yaml").resolve()
    logger.info("Using defaults from %s.", in_file)
    dest_path = Path(arguments.get("--out-dir", ".") or ".")
    if dest_path.exists() and dest_path.is_dir():
        file_name = arguments.get("--mode", "configuration") or "configuration"
        dest_file = (dest_path / f"{file_name}.yaml").resolve()
        # Now copy the template file to the given out file
        logger.info("Writing template configuration to %s", dest_file)
        with open(in_file, "r") as fin:
            dest_file.write_text(fin.read())
    else:
        logger.error(
            "Couldn't create configuration file. Out dir doesn't exist or is no directory."
        )


def run():
    """
    Runs the server
    """
    # from digicubes_rest.web import create_app

    server = DigiCubeServer()

    # Checks if the web frontend should be mounted
    # Defaults to no.
    # if server.config.get("mount_web_app", False):
    #    mountpoint = server.config.get("web_app_mount_point", "/web")
    #    logger.info("Mounting web app. Mount point is: %s", mountpoint)
    #    server.mount(mountpoint, create_app())

    # Check, if we should setup the graphql route
    # Defaults to False.
    # if server.config.get("mount_graphql", False):
    #    mountpoint = server.config.get("graphql_mount_point", "/graphql")
    #    view = responder.ext.GraphQLView(api=server.api, schema=schema)
    #    server.api.add_route(mountpoint, view)

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
