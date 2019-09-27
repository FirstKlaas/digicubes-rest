import logging

from . import DigiCubeServer

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


def run():
    from digicubes.web import create_app

    server = DigiCubeServer()

    if server.config.get("mount_web_app", False):
        mountpoint = server.config.get("web_app_mount_point", "/web")
        logger.info("Mounting web app. Mount point is: %s", mountpoint)
        server.mount(mountpoint, create_app())

    server.run()
