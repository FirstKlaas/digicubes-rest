# pylint: disable=C0111


class DigiCubeError(Exception):
    """
    The base exception class for digicubes
    """


class ConstraintViolation(DigiCubeError):
    """
    This exception is raised, when a model
    constraint is violated.
    """


class ServerError(DigiCubeError):
    """
    This exception is raised, when a server error
    occurred.
    """


class DoesNotExist(DigiCubeError):
    """
    Raised, when a ressource is not avaliable
    on the server. Typically when the servers
    sends back a 404 response.
    """


class InsufficientRights(DigiCubeError):
    """
    The user has not the necessary rights
    """


class TokenExpired(DigiCubeError):
    """
    The bearer token has expired. A fresh login
    is needed.
    """


class BadPassword(DigiCubeError):
    """Wrong password"""


class NotAuthenticated(DigiCubeError):
    """User is not logged in"""
