import os

from importlib.resources import read_text


def copy_templates():

    configpath = os.environ.get("DIGICUBES_CONFIG_PATH", "cfg")
    settings = read_text("digicubes_rest.server.cfg.templates", "configuration.yaml")
    print(settings)
