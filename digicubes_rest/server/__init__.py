# pylint: disable=missing-docstring
"""Testclient"""
from datetime import timedelta, datetime
import logging
import logging.config
import random
import string

from importlib.resources import open_text
import os
import re
from pathlib import Path

import jwt
from dotenv import load_dotenv
import responder

from starlette.middleware.base import BaseHTTPMiddleware

from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

import yaml

from digicubes_rest.exceptions import DigiCubeError
from digicubes_rest.storage import models
from digicubes_rest.server import ressource as endpoint
from digicubes_rest.server.middleware import SettingsMiddleware, UpdateTokenMiddleware
from digicubes_rest.server.ressource import util

logger = logging.getLogger(__name__)


class DigiCubeServer:
    """
    The DigiCubes Server
    """

    def __init__(self):
        # Initializing settings

        # First load environment variables from a .env file if exists.
        # So the .env file has a higher precedence over preset
        # environment variables
        load_dotenv(verbose=True)
        self.port = os.environ.get("DIGICUBES_PORT", 3548)
        self.address = "0.0.0.0"
        secret_key = os.environ.get("DIGICUBES_SECRET", "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o")
        db_url = os.environ.get("DIGICUBES_DATABASE_URL", "sqlite://:memory:")
        modules = {
            "model": ["digicubes_rest.storage.models"],
        }

        async def onStartup():
            """
            Initialise the database during startup of the webserver.
            """
            logger.info("Using database url %s", db_url)
            await Tortoise.init(db_url=db_url, modules=modules)
            await Tortoise.generate_schemas()

        async def onShutdown():
            """
            Shutdown the database during startup of the webserver.
            """
            await Tortoise.close_connections()

        # Now setup responder
        self.api = responder.API(secret_key=secret_key)
        self.api.add_event_handler("startup", onStartup)
        self.api.add_event_handler("shutdown", onShutdown)

        # Adding a middleware to add the api to the request state
        settings = {
            "default_count": 10,
            "max_count": 100,
        }
        self.api.add_middleware(SettingsMiddleware, settings=settings, api=self.api)

        # Add all the routes to the api
        endpoint.add_routes(self.api)

        @self.api.route("/")
        async def home(
            req: responder.Request, resp: responder.Response
        ):  # pylint: disable=unused-variable, unused-argument
            resp.text = "Hello World"

        @self.api.route("/verify/user/{data}")
        async def verify_user(
            req: responder.Request, resp: responder.Response, *, data
        ):  # pylint: disable=unused-variable, unused-argument

            if req.method == "get":
                # Generate a verification token for this user.

                # First check, if the user exists
                user = await models.User.get_or_none(id=int(data))

                if user is None:
                    resp.status_code = 404
                    resp.text = f"User with id {data} not found."

                else:
                    lifetime = timedelta(hours=6)  # TODO: make this configurable

                    # The user may or may not be verified.
                    # Also the state of the user is set to "not verified".
                    # Because only active user can verify,
                    # the user is set so active.
                    user.is_verified = False
                    user.is_active = True
                    await user.save()

                    payload = {}
                    payload["user_id"] = user.id
                    payload["exp"] = datetime.utcnow() + lifetime
                    payload["iat"] = datetime.utcnow()
                    token = jwt.encode(payload, self.secret_key, algorithm="HS256")
                    resp.media = {"token": token.decode("UTF-8"), "user_id": int(data)}

            elif req.method == "put":
                # Check the provided token and verify the user.
                try:
                    token = str(data)
                    payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                    user_id = payload["user_id"]

                    user = await models.User.get_or_none(id=user_id)
                    if user is None:
                        resp.status_code = 404
                        resp.text = f"No user with id {user_id} found"
                    else:
                        user.is_verified = True
                        user.is_active = True
                        await user.save()
                        credentials = self.createBearerToken(user_id=user.id)
                        resp.media = {
                            "user": user.unstructure(exclude_fields=["password_hash"]),
                            "token": credentials.bearer_token,
                        }
                except:  # pylint: disable=bare-except
                    logger.exception("Could not verify.")

            else:
                resp.status_code = 405
                resp.text = f"Method {req.method} not allowed."

        self._extensions = []

    def add_extension(self, extension):
        logger.info("Register extension %r", type(extension))
        self._extensions.append(extension)

    @property
    def secret_key(self):
        """
        Returns the secret key.

        The key is used as secret for jwt decoding and encoding. It is also the secret
        key of the responder.API()
        """
        return self.api.secret_key

    def run(self):
        """
        Run the DigiCubeServer
        """
        # First init all extensions
        for extension in self._extensions:
            logger.info("Initialise extension %r.", type(extension))
            extension.init(self)

        # Now start the server
        logger.info("Starting digicubes server on port %d.", self.port)
        self.api.run(port=self.port, address=self.address, debug=True)

    def createBearerToken(self, user_id: int, minutes=30, **kwargs) -> str:
        """Create a bearer token used for authentificated calls."""
        return util.create_bearer_token(
            user_id, secret=self.secret_key, lifetime=timedelta(minutes=minutes), **kwargs
        )

    def decodeBearerToken(self, token: str) -> str:
        """Decode a bearer token"""
        return util.decode_bearer_token(token, self.secret_key)

    def mount(self, route, app):
        """Mounts an WSGI / ASGI application at a given route.

        :param route: String representation of the route to be used (shouldn't be parameterized).
        :param app: The other WSGI / ASGI app.
        """
        self.api.mount(route, app)
