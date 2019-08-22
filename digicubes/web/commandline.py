import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(logging.INFO)

def run():
    from digicubes.web import create_app
    logger.info("Starting the digicubes webserver")
    app = create_app()
    app.run()
