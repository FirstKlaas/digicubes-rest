import functools
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

def needs_apikey():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(req, resp, *args, **kwargs):
            # apikey = req.headers.get('digicubes-apikey', None)
            # if apikey is None:
            #    resp.status_code = 500
            #    return
            print(req.method)
            await func(req, resp, *args, **kwargs)

        return wrapper

    return decorator


def needs_valid_token():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(req, resp, *args, **kwargs):
            # apikey = req.headers.get('digicubes-apikey', None)
            # if apikey is None:
            #    resp.status_code = 500
            #    return
            await func(req, resp, *args, **kwargs)

        return wrapper

    return decorator


class BasicRessource:

    X_FILTER_FIELDS = "x-filter-fields"

    @property
    def route(self):
        return getattr(self, "route", None)

    @property
    def prefix(self):
        return getattr(self, "prefix", None)

    @property
    def ressource_path(self):
        return self.prefix + self.route

    def get_filter_fields(self, req: str) -> Optional[List[str]]:
        x_filter_fields = req.headers.get(BasicRessource.X_FILTER_FIELDS, None)
        logger.warn(f"x_filter_fields: {x_filter_fields}")
        if x_filter_fields is not None:
            fields = x_filter_fields.split(",")
            if "id" not in fields:
                fields.append("id")
            logger.debug(f"filter_fields: {fields}")
            return fields

        return None

    async def on_delete(self, req, resp):
        resp.status_code = 405

    def get_base_url(self, req):
        return f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}"


def error_response(resp, code, text):
    resp.media = {"errors": [{"msg": text}]}
    resp.status_code = code
