# pylint: disable=C0111
import functools
import logging
from typing import Optional, List

from tortoise import transactions
from tortoise.exceptions import IntegrityError

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
        Returns a list of fileterd fields
        """
        x_filter_fields = req.headers.get(BasicRessource.X_FILTER_FIELDS, None)
        logger.warning("x_filter_fields: %s", x_filter_fields)
        if x_filter_fields is not None:
            fields = x_filter_fields.split(",")
            if "id" not in fields:
                fields.append("id")
            logger.debug("filter_fields: %s", fields)
            return fields

        return None

    def get_base_url(self, req):
        # pylint: disable=R0201
        return f"{req.url.scheme}://{req.url.host}:{req.url.port}{req.url.path}"


def error_response(resp, code, text):
    resp.text = text
    resp.status_code = code


async def create_ressource(cls, data): #pylint: disable=too-many-return-statements
    """
    Generic ressource creation
    """
    if isinstance(data, dict):
        try:
            res = cls.structure(data)
            await res.save()

            return (201, res.unstructure())

        except IntegrityError as error:
            return (400, str(error))
        except Exception as error:  # pylint: disable=W0703
            return (500, str(error))

    elif isinstance(data, list):
        # Bulk creation of schools
        transaction = await transactions.start_transaction()
        try:
            res = [cls.structure(item) for item in data]
            await cls.bulk_create(res)
            await transaction.commit()
            return (201, None)

        except IntegrityError as error:
            await transaction.rollback()
            return (409, str(error))

        except Exception as error:  # pylint: disable=W0703
            await transaction.rollback()
            return (400, str(error))

    else:
        return(500, f"Unsupported data type {type(data)}")
