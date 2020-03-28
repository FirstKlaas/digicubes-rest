import argparse
import logging
import os

from importlib.resources import read_text

from . import DigiCubeServer

logger = logging.getLogger(__name__)


def evaluate_command():
    """
    Evaluates the commandline.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show some more output.", action="store_true")
    parser.add_argument("cmd", help="The command [start|setup]", type=str)
    args = parser.parse_args()
    # print(args)

    if args.cmd == "run":
        run()
    elif args.cmd == "setup":
        cfg(args)
    else:
        print(f"Unknown command {args.cmd}")


def cfg(arguments):
    configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")
    settings = read_text("digicubes_rest.server.cfg.templates", "configuration.yaml")
    os.makedirs(configpath, exist_ok=True)
    file_path = os.path.join(configpath, "configuration.yaml")
    with open(file_path, "wt") as f:
        f.write(settings)


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
