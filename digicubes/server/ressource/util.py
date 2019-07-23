# pylint: disable=C0111
import functools
import logging
from typing import Optional, List

from responder import Response

from tortoise import transactions
from tortoise.models import ModelMeta, Model
from tortoise.exceptions import IntegrityError

from werkzeug import http

logger = logging.getLogger(__name__)  # pylint: disable=C0103


def needs_apikey():
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
    # pylint: disable=C0103
    def __init__(self, name, parameter_type):
        self.name = name
        self.parameter_type = parameter_type

    def __call__(self, f):
        async def wrapped_f(me, req, resp, *args, **kwargs):
            if self.name not in kwargs:
                msg = "Parameter <%s> not present in named parameters. Got %s" % (
                    self.name,
                    list(kwargs.keys()),
                )
                error_response(resp, 404, msg)
                return

            try:
                v = self.parameter_type(kwargs[self.name])
                kwargs[self.name] = v
            except ValueError:
                msg = "Expected parameter <%s> to be of type <%s>" % (
                    self.name,
                    self.parameter_type.__name__,
                )
                error_response(resp, 404, msg)
                return
            return await f(me, req, resp, *args, **kwargs)

        wrapped_f.__doc__ = f.__doc__
        return wrapped_f


class needs_int_parameter(needs_typed_parameter):
    # pylint: disable=C0103
    def __init__(self, name):
        """
        A version especially for int parameters.
        """
        super().__init__(name, type(0))


class BasicRessource:
    """
    A base for all endpoints
    """

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
        # pylint: disable=R0201
        """
        Returns a list of filtered fields. The basevalue is taken
        from the header field ``
        """
        x_filter_fields = req.headers.get(BasicRessource.X_FILTER_FIELDS, None)
        logger.debug("%s: %s", BasicRessource.X_FILTER_FIELDS, x_filter_fields)
        if x_filter_fields is not None:
            fields = x_filter_fields.split(",")
            if "id" not in fields:
                fields.append("id")
            logger.debug("%s: %s", BasicRessource.X_FILTER_FIELDS, fields)
            return [field.strip() for field in fields]

        return None

    def set_timestamp(self, resp: Response, model: Model) -> None:
        """
        Set the ```Last-Modified`` to reflect the ``modified_at`` attribute
        of the model, if present.
        """
        # pylint: disable=R0201
        if hasattr(model, "modified_at"):
            resp.headers["Last-Modified"] = http.http_date(model.modified_at)
            if hasattr(model, "id"):
                raw = "{:#<10}{:0<10}{}".format(
                    model.__class__.__name__, model.id, http.http_date(model.modified_at)
                )
                resp.headers["ETag"] = http.generate_etag(raw.encode())

    def get_base_url(self, req):
        # pylint: disable=R0201
        return f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}"


def error_response(resp, code, text=None, error=None):
    msg = {}

    if text is not None:
        msg["msg"] = text
        if error is not None:
            msg["error"] = str(error)
    elif error is not None:
        msg["msg"] = str(error)
    else:
        msg = None

    resp.media = msg
    resp.status_code = code


async def create_ressource(cls, data, filter_fields=None):
    # pylint: disable=too-many-return-statements
    """
    Generic ressource creation
    """
    if not isinstance(cls, ModelMeta):
        raise ValueError(
            "Parameter cls expected to be of type ModelMeta. But type is %s" % type(cls)
        )

    transaction = await transactions.start_transaction()
    try:
        if isinstance(data, dict):
            res = cls.structure(data)
            await res.save()
            await transaction.commit()
            return (201, res.unstructure(filter_fields))

        if isinstance(data, list):
            # Bulk creation of schools
            res = [cls.structure(item) for item in data]
            await cls.bulk_create(res)
            await transaction.commit()
            return (201, None)

        await transaction.rollback()
        return (500, f"Unsupported data type {type(data)}")

    except IntegrityError as error:
        await transaction.rollback()
        return (409, str(error))

    except Exception as error:  # pylint: disable=W0703
        await transaction.rollback()
        return (400, str(error))
