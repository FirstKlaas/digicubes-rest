"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import logging
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request

from .util import digi_client, DigicubesAccountManager

from .contants import TOKEN_COOKIE_NAME

logger = logging.getLogger(__name__)

account_manager = DigicubesAccountManager()


def create_app(config_filename="production"):
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    app.config.from_object("digicubes.web.contants")
    for key, value in app.config.items():
        print(f"{key:<40}{value}")
    account_manager.init_app(app)

    logger.debug("Static folder is %s", app.static_folder)
    return app
