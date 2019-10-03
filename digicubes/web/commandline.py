"""
digiweb

Usage:
  digiweb --template=<name>
  digiweb [--config=<name>] [-d | --development | -p | --production | -t | --testing]

Options:
  --template=<name>   Name of a file to write default settings to. Defaults to 'account.yaml'
  --config=<name>     Name of the configuration file. Defaults to 'digicubes.yaml'
  -d --development  Starts the server in development mode
  -p --production   Starts the server in production mode (default)
  -t --testing      Starts the server in testing mode
"""
import logging
import os
from os.path import isfile

from docopt import docopt
import yaml

from digicubes.web.modules.account.config import AccountConfig

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_account_defaults():
    """
    Return the defaults for the account module"""
    return {key: value for key, value in AccountConfig.__dict__.items() if not key.startswith("_")}


def export_account_defaults(filename):
    """
    Writes the configuration options for
    the account module to the specified file.
    """
    if not filename.endswith(".yaml"):
        filename = filename + ".yaml"

    i = get_account_defaults()
    with open(filename, "w") as f:
        yaml.dump(i, f, default_flow_style=False)


def config_from_yaml(app, filename):
    """
    Configures the server based on a yaml file
    """

    if not filename.endswith(".yaml"):
        filename = filename + ".yaml"

    if isfile(filename):
        with open(filename) as f:
            config = yaml.load(f)
            env = app.config["ENV"].upper()
            logger.info("Starting server in %s mode.", env)
            settings = config.get(env.upper())
            if settings is not None:
                app.config.update(settings)
    else:
        logger.error("Config file %s was specified, but does not exists")


def run():
    """Runs the server"""
    from digicubes.web import create_app

    arguments = docopt(__doc__, help=True, version="Run DigiCubes Webserver 1.0")

    # Setting up the environment
    if arguments["--development"]:
        os.environ["FLASK_ENV"] = "development"
    elif arguments["--testing"]:
        os.environ["FLASK_ENV"] = "testing"
    else:
        os.environ["FLASK_ENV"] = "production"

    template = arguments.get("--template", None)
    if template is not None:
        export_account_defaults(template)
    else:
        logger.info("Starting the digicubes webserver")
        app = create_app()
        config_file = arguments.get("--config")
        if config_file is not None:
            config_from_yaml(app, config_file)

        app.run()


if __name__ == "__main__":
    run()
