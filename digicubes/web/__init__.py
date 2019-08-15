import logging
from typing import Optional

from flask import Flask, redirect, url_for, Response, request, Request

from .blueprints import admin, home
from .util import digi_client, DigicubesAccountManager

from .contants import (
    TOKEN_COOKIE_NAME
)

logger = logging.getLogger(__name__)

account_manager = DigicubesAccountManager()

@account_manager.unauthorized_handler
def neenee():
    return redirect("/login")


@account_manager.successful_logged_in_handler
def after_login():
    return redirect("/")

def create_app(config_filename='production'):
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #TODO: Set via configuration
    app.config.from_object('digicubes.web.contants')
    for key, value in app.config.items():
        print(f"{key:<40}{value}")
    account_manager.init_app(app)

    logger.debug("Static folder is %s", app.static_folder)
    return app
