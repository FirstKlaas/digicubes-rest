import logging
import yaml
from os.path import isfile

from digicubes.web.modules.account.config import AccountConfig

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_account_defaults():
    return {
        key: value for key, value in AccountConfig.__dict__.items() if not key.startswith("_")
    }

def export_account_defaults(filename):
    i = get_account_defaults()
    d = {
        "MODULE_ACCOUNT_DEFAULTS" : i,
        "PRODUCTION" : i,
        "DEVELOPMENT" : i
    }
    with open(filename, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)
    
    print(yaml.dump(d, default_flow_style=False))

def config_from_yaml(app, filename=None):

    if isfile(filename):
        with open(filename) as f:
            config = yaml.load(f)
            env = app.config["ENV"].upper()
            logger.info("Starting server in %s mode.", env)
            settings = config.get(env.upper())
            app.config.update(settings)


def run():
    from digicubes.web import create_app

    logger.info("Starting the digicubes webserver")
    app = create_app()
    config_from_yaml(app, "config.yaml")
    app.config.update(get_account_defaults())
    export_account_defaults('test.yaml')
    # app.run()

if __name__ == "__main__":
    run()
