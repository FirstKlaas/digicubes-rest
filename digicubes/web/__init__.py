"""
A minimal startscript for the server. This can be used
as a quickstart module.
"""
import logging
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request

from .account import DigicubesAccountManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

account_manager = DigicubesAccountManager()


def create_app():
    """
    Factory function to create the flask server.
    Flask will automatically detect the method
    on `flask run`.
    """
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # TODO: Set via configuration
    account_manager.init_app(app)
    # for key, value in app.config.items():
    #    logger.debug("%s: %s", key, value)

    logger.debug("Static folder is %s", app.static_folder)
    return app
