# pylint: disable=C0111
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Union

import jwt
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist
from werkzeug import http
from responder import Request, Response

from digicubes.storage import models
from digicubes.storage.pools import UserPool
from digicubes.common.exceptions import InsufficientRights
from digicubes.common.entities import RightEntity

logger = logging.getLogger(__name__)  # pylint: disable=C0103
# logger.setLevel(logging.DEBUG)

TRights = Optional[Union[Union[RightEntity, str], List[Union[RightEntity, str]]]]


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


def create_bearer_token(user_id: int, secret: str, lifetime: timedelta = None, **kwargs) -> str:
    """
    Create a bearer token used for authentificated calls.

    The ``iat`` (issued at time) field is automatically set to current
    utc time. The parameter ``lifetime`` specifies how long the token
    will be valid. If used after that period, a
    :py:class:`~jwt.ExpiredSignatureError` will be raised.
    The default lifetime is 30 minutes.

    :param int user_id: The database id of the user.
    :param str secret: The secret used to generate the token.
    :param datetime.timedelta lifetime: The lifetime of the token after which it expires

    :return: The generated token.
    :rtype: str
    """
    if lifetime is None:
        # Setting the lifetime default
        lifetime = timedelta(minutes=30)

    payload = {}
    payload.update(**kwargs)

    payload["user_id"] = user_id
    payload["exp"] = datetime.utcnow() + lifetime
    payload["iat"] = datetime.utcnow()
    logger.debug("iat = %s", datetime.utcnow())
    token = jwt.encode(payload, secret, algorithm="HS256")
    logger.debug("Generated token is %s", token.decode("UTF-8"))
    return token.decode("UTF-8")


def decode_bearer_token(token: str, secret: str) -> str:
    """
    Decode a bearer token

    The bearer token is decoded and the payload is returned.
    The secret has to be the same secret used for creating the token.

    :param str token: The token to be decoded.
    :param str secret: The secret used for decoding.

    :return: The payload of the decoded token.
    :rtype: str

    :raises jwt.exceptions.ExpiredSignatureError: If the token is not valid anymore
    """
    # TODO: Is it really str wich will be returned? What if the encoded payload was a dict?
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload


async def get_user_rights(user: models.User) -> List[str]:
    """
    Get a flat list of user rights, associated with the ``user``.

    :param digicubes.storage.models.User user: Get the rights for this user.

    :return: A list of rights associated with this user.
    :rtype: list(str)
    """
    return (
        await models.Right.filter(roles__users__id=user.id)
        .distinct()
        .values_list("name", flat=True)
    )


async def check_rights(user: models.User, rights: List[Union[RightEntity, str]]) -> List[str]:
    """
    Returns the intersection of the user rights and the
    rights in the parameter rights.
    """
    logger.debug("Checking rights for user %s", user.login)
    # If no rights to test, the answer is pretty clear
    if not rights:
        return []

    rights_list = await get_user_rights(user)
    logger.debug("The full list of user rights is: %s", rights_list)
    # Make a pure stringlist from the rightslist, as it may be
    # a mixture of strings and RightEntity entries.
    rights = [right if isinstance(right, str) else right.name for right in rights]

    # if only one right is tested, we can simply do an in test.
    if len(rights) == 1 and rights[0] in rights_list:
        return rights

    # No we need the intersection between the user rights
    # and the test rights
    return list(set(rights_list) & set(rights))


async def has_right(user: models.User, rights: List[str]) -> bool:
    """
    Test, if the user has at least one of the rights.
    """
    return len(await check_rights(user, rights)) > 0


async def is_root(user: models.User) -> bool:
    """
    Test if the user has root rights.
    """
    return await has_right(user, [RightEntity.ROOT_RIGHT])


class needs_bearer_token:

    __slots__ = ["rights"]

    def __init__(self, rights: TRights = None) -> None:
        if rights is None:
            self.rights = None
        elif isinstance(rights, (str, RightEntity)):
            self.rights = [rights, RightEntity.ROOT_RIGHT]
        else:
            self.rights = rights + [RightEntity.ROOT_RIGHT]

    def __call__(self, f):  # pylint: disable=R0915
        async def wrapped_f(me, req: Request, resp: Response, *args, **kwargs):
            # pylint: disable=too-many-branches
            resp.status_code = 401
            try:
                # Check the header.
                bearer = req.headers["Authorization"]
                scheme, token = bearer.split(" ")
                logger.debug("We have a scheme and a token")
                # We could and we should do more test if
                # the provided token is correct formatted.
                if scheme == "Bearer":
                    # Currently only the Bearer scheme
                    try:
                        payload = decode_bearer_token(token, req.api.secret_key)
                        user_id = payload.get("user_id", None)
                        logger.debug("Token %s", token)
                        logger.debug("We have a valid bearer token and the id is %d", user_id)
                        if user_id is None:
                            raise jwt.DecodeError()

                        # Now we need the user
                        # user = await UserPool.get_user(user_id)
                        user = await models.User.get(id=user_id)
                        logger.debug("We have a user. The login is %s", user.login)

                        # Let's see, if we have to check some rights
                        logger.debug("Now see, if the user has one of the rights: %s", self.rights)
                        if self.rights is not None:
                            # Yes, we have to
                            needed_rights = await check_rights(user, self.rights)
                            logger.debug("Matching rights: %s", needed_rights)
                            if not needed_rights:
                                # None of the requierements are fullfilled
                                raise InsufficientRights(
                                    f"User has non of the following rights {self.rights}"
                                )
                            # If the calling instance has a user_right attribute,
                            # subset of requested rights, the user has are stored
                            # in that attribute
                            if hasattr(me, "user_rights"):
                                setattr(me, "user_rights", needed_rights)

                            # Also save the rights to the request state
                            req.state.user_rights = needed_rights

                        # The current user is stored in the calling instance, if the
                        # instance has a current_user attribute, which is true for all
                        # Classes derived from BaseRessource
                        if hasattr(me, "current_user"):
                            setattr(me, "current_user", user)

                        # Saving the current user in the request state
                        req.state.current_user = user

                        # newkwargs.update(kwargs)
                        # Everythings fine
                        resp.status_code = 200
                        logger.debug("Caller class: %r", me)
                        return await f(me, req, resp, *args, **kwargs)

                    except jwt.ExpiredSignatureError:
                        resp.text = "Token expired"
                    except jwt.DecodeError:
                        resp.text = "Bad bearer token"
                    except DoesNotExist:
                        resp.text = "No such user"
                    except InsufficientRights as error:
                        resp.text = str(error)
                else:
                    resp.text = f"Unknown ot unsupported authorization scheme. {scheme}"
            except KeyError:
                resp.text = "No authorization header provided"
            except (ValueError, Exception):  # pylint: disable=broad-except
                logger.exception("Something went wrong")
                resp.status_code = 400
                resp.text = "Bad Request"

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

    __slots__ = ["current_user", "user_rights"]

    def __init__(self):
        self.current_user = None
        self.user_rights = None

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

    def get_user(self, user_id: int) -> models.User:  # pylint: disable=no-self-use
        """
        Returns a user for a given id or throws
        a DoesNotExist exception if no user with the given
        id exists.
        """
        return UserPool.get_user(user_id)


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
