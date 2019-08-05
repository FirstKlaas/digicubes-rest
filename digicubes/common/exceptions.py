# pylint: disable=C0111


class InsufficientRights(Exception):
    """
    The user has not the necessary rights
    """


class TokenExpired(Exception):
    """
    The bearer token has expired. A fresh login
    is needed.
    """


class ServerError(Exception):
    """
    A server error occurred
    """
