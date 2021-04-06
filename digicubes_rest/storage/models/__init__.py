"""All models for the digicubes plattform"""

from .apikey import ApiKey
from .org import Right, Role, User
from .school import Course, School, Unit

__all__ = [User, Role, Right, School, Course, ApiKey, Unit]
