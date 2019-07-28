# pylint: disable=C0111
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Union

from responder import Response
import jwt

from tortoise import transactions
from tortoise.models import ModelMeta, Model
from tortoise.exceptions import IntegrityError, DoesNotExist

from werkzeug import http

from digicubes.storage.models import User, Right
from digicubes.common.exceptions import InsufficientRights

logger = logging.getLogger(__name__)  # pylint: disable=C0103

TRights = Optional[Union[str, List[str]]]


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


def createBearerToken(user_id: int, secret: str, minutes=30, **kwargs) -> str:
    """Create a bearer token used for authentificated calls."""
    payload = {"user_id": user_id}
    for key, value in kwargs.items():
        payload[key] = value
    payload["exp"] = datetime.utcnow() + timedelta(minutes=minutes)
    payload["iat"] = datetime.utcnow()
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token.decode("UTF-8")


def decodeBearerToken(token: str, secret: str) -> str:
    """Decode a bearer token"""
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload


async def check_rights(user: User, rights: List[str]):
    """
    Returns the intersection of the user rights and the
    rights in the parameter rights.
    """
    # TODO: Write a test case
    # TODO: Use the Right enum instead of strings

    # If no rights to test, the answer is pretty clear
    if not rights:
        return []

    rights_dict = await Right.filter(roles__users__id=1).distinct().values("name")
    rights_list = [right["name"] for right in rights_dict]

    # if only one right is tested, we can simply do an in test.
    if len(rights) == 1:
        return rights[0] in rights_list

    # No we need the intersection between the user rights
    # and the test rights
    return list(set(rights_list) & set(rights))


async def has_right(user: User, rights: List[str]):
    """
    Test, if the user has at least one of the rights.
    """
    # TODO: Write a test case.
    return len(check_rights) > 0


class needs_bearer_token:

    __slots__ = ["rights"]

    def __init__(self, rights: TRights = None) -> None:
        if rights is None:
            self.rights = None
        elif isinstance(rights, str):
            self.rights = [rights]
        else:
            self.rights = [right for right in rights]

    def __call__(self, f):
        async def wrapped_f(me, req, resp, *args, **kwargs):
            resp.status_code = 401
            try:
                # Check the header.
                bearer = req.headers["Authorization"]
                scheme, token = bearer.split(" ")
                # We could and we should do more test if
                # the provided token is correct formatted.
                if scheme == "Bearer":
                    # Currently only the Bearer scheme
                    try:
                        payload = decodeBearerToken(token, req.api.secret_key)
                        user_id = payload.get("user_id", None)

                        if user_id is None:
                            raise jwt.DecodeError()

                        # Now we need the user
                        user = await User.get(id=user_id)

                        # Let's see, if we have to check some rights
                        if self.rights is not None:
                            # Yes, we have to
                            needed_rights = check_rights(user, self.rights)
                            if not needed_rights:
                                # None of the requierements are fullfilled
                                raise InsufficientRights(
                                    f"User has non of the following rights {self.rights}"
                                )

                        # If requested, write the intersecting rights
                        # to the named args. This can be used in the decorated
                        # function to do different opererations, depending
                        # on the differents rights.
                        if hasattr(kwargs, "rights"):
                            kwargs["rights"] = needed_rights

                        # If requested, write the user back to the named args
                        if hasattr(kwargs, "current_user"):
                            kwargs["current_user"] = user

                        # Everythings fine
                        resp.status_code = 200
                        return await f(me, req, resp, *args, **kwargs)

                    except jwt.ExpiredSignatureError:
                        resp.text = "Token expired"
                    except jwt.DecodeError:
                        resp.text = "Bad bearer token"
                    except DoesNotExist:
                        resp.text = "No such user"
                else:
                    resp.text = f"Unknown ot unsupported authorization scheme. {scheme}"
            except KeyError:
                resp.text = "No authorization header provided"

        wrapped_f.__doc__ = f.__doc__
        return wrapped_f


class needs_right:
    def __init__(self, name):
        self.name = name

    def __call__(self, f):
        async def wrapped_f(me, req, resp, *args, **kwargs):
            print("inside wrapped")
            if "user_id" not in kwargs:
                msg = "No user_id provided to check right '%s'. Got %s" % (
                    self.name,
                    list(kwargs.keys()),
                )
                error_response(resp, 404, msg)
                return

            try:
                pass
            except ValueError:
                error_response(resp, 404, "")
                return
            return await f(me, req, resp, *args, **kwargs)

        wrapped_f.__doc__ = f.__doc__
        return wrapped_f


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

            # Setting an ETag, which identifies the ressource in time.
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
