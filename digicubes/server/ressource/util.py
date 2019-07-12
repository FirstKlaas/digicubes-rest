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


class needs_typed_parameter:
    def __init__(self, name, parameter_type):
        self.name = name
        self.parameter_type = parameter_type

    def __call__(self, f):
        async def wrapped_f(me, req, resp, *args, **kwargs):
            if self.name not in kwargs:
                resp.status_code = 404
                resp.text = f"Parameter <{self.name}> not present in named parameters. Got {list(kwargs.keys())}"
                return

            try:
                v = self.parameter_type(kwargs[self.name])
                kwargs[self.name] = v
            except ValueError:
                resp.status_code = 404
                resp.text = f"Expected parameter <{self.name}> to be of type <{self.parameter_type.__name__}>"
                return
            return await f(me, req, resp, *args, **kwargs)

        return wrapped_f


class needs_int_parameter(needs_typed_parameter):
    def __init__(self, name):
        super().__init__(name, type(0))


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
        logger.warn("x_filter_fields: %s" % x_filter_fields)
        if x_filter_fields is not None:
            fields = x_filter_fields.split(",")
            if "id" not in fields:
                fields.append("id")
            logger.debug("filter_fields: %s" % fields)
            return fields

        return None

    async def on_delete(self, req, resp):
        resp.status_code = 405

    def get_base_url(self, req):
        return f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}"


def error_response(resp, code, text):
    resp.media = {"errors": [{"msg": text}]}
    resp.status_code = code
