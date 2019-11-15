"""
Defaults for the api server
"""

SIMPLE_SETTINGS = {"OVERRIDE_BY_ENV": True, "CONFIGURE_LOGGING": True}

# Limit the number of records returned in a response.
request = {"max_count": 100, "default_count": 10}

# Enable the standard frontend.
web_app = {"mount": False, "route": "/web"}

# Enable graphql. This is highly experimental
# Don't activate it in production environment.
graphql = {"mount": False, "route": "/graphql"}

# The port, ther server is listening on.
port = 3000

# Database URL
db_url = "sqlite://digicubes.db"

# Secret to be used to encrypt data.
secret = "b3j6casjk7d8szeuwz00hdhuw4ohwDu9o"
