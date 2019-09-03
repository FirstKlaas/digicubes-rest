from . import DigiCubeServer


def run():
    from digicubes.web import create_app
    server = DigiCubeServer()
    server.mount("/web", create_app())
    server.run()
