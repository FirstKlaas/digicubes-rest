"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import logging
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request

from .account import DigicubesAccountManager

from .defaults import TOKEN_COOKIE_NAME

logger = logging.getLogger(__name__)

account_manager = DigicubesAccountManager()

logging.basicConfig(level=logging.DEBUG)

def create_app(config_filename="production"):
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    app.config.from_object("digicubes.web.defaults")
    for key, value in app.config.items():
        logger.debug("%s: %s", key, value)

    account_manager.init_app(app)

    logger.debug("Static folder is %s", app.static_folder)
    return app
