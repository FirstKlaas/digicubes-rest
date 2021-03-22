# pylint: disable=redefined-outer-name
#
import pytest
from digicubes_rest.server import DigiCubeServer


@pytest.fixture
def api():
    server = DigiCubeServer()
    yield server.api


def test_hello_world(api):
    r = api.requests.get("/")
    assert r.text == "Hello World"
