import logging

from responder.core import Request, Response

from digicubes_rest.storage.models import User, Role
from .util import BasicRessource, needs_bearer_token


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


# @needs_bearer_token()
class InfoRessource(BasicRessource):
    async def on_get(self, req: Request, resp: Response) -> None:

        what = req.params.get("w", None)

        if what == "home_routes":
            routes = {}
            for role in await Role.all():
                routes[role.name] = role.home_route

            resp.media = {"home_routes": routes}

        else:
            resp.status_code = 404  # File not found
            resp.text = f"I do not understand {what}"
