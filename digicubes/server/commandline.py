import logging

from . import DigiCubeServer

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

def run():
    from digicubes.web import create_app
    server = DigiCubeServer()

    if server.config.get("MOUNT_WEB_APP", False):
        server.mount("/web", create_app())
    
    server.run()
