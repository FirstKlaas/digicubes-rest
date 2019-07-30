"""All models for the digicubes plattform"""

from .org import User, Role, Right, hash_password, verify_password
from .school import School, Course

from .apikey import ApiKey
