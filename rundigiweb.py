import os
from digicubes_rest.web.commandline import run

os.putenv("FLASK_ENV", "development")

run()
