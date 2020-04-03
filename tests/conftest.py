import pytest

from digicubes_rest.server import DigiCubeServer

@pytest.fixture(scope="session", autouse=True)
def server():
    print("Requested Server")
    return DigiCubeServer()


