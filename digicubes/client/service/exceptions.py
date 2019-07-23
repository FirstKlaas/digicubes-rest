"""
All exceptions
"""


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
