import logging

from flask import Flask, render_template, url_for, request

from digicubes.server import DigiCubeServer

logger = logging.getLogger(__name__)

class DigiWeb:
    def __init__(self):
        #FIXME: This kind of relative path is evil.
        #       And how to change via setting?
        self.flask = Flask(__name__)
        logger.debug("Static folder is %s",self.flask.static_folder)

    def init(self, server):
        @self.flask.route('/')
        def hello():
            print(type(request))
            return render_template("root/base.jinja")

        server.mount("/digiweb", self.flask)
