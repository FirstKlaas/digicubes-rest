"""All models for the digicubes plattform"""

from .org import User, Role, Right
from .school import School, Course

from .apikey import ApiKey

__ALL__ = ["User", "Role", "Right", "School", "Course", "ApiKey"]
