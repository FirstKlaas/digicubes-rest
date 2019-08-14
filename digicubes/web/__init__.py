import logging

from flask import Flask

from .blueprints import admin
from .util import digi_client, LoginManager

logger = logging.getLogger(__name__)

login_manager = LoginManager()

@login_manager.unauthorized_handler
def neenee():
    return "Do kommst hier nicht rein."

def create_app(config_filename='production'):
    app = Flask(__name__)
    login_manager.init_app(app)
    app.register_blueprint(admin, url_prefix="/admin")

    @app.context_processor
    def context():
        return {
            "digi_client" : digi_client,
            "moin" : "klaas"
        }

    logger.debug("Static folder is %s", app.static_folder)
    return app
