import logging

from flask import Flask, redirect, url_for

from .blueprints import admin, home
from .util import digi_client, LoginManager

logger = logging.getLogger(__name__)

login_manager = LoginManager()

@login_manager.unauthorized_handler
def neenee():
    return redirect("/login")

def create_app(config_filename='production'):
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #TODO: Set via configuration
    login_manager.init_app(app)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(home, url_prefix="/")

    @app.context_processor
    def context():
        return {
            "digi_client" : digi_client,
            "moin" : "klaas"
        }

    logger.debug("Static folder is %s", app.static_folder)
    return app
