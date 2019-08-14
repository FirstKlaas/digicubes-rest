import os
from digicubes.web import create_app

os.putenv("FLASK_ENV", "development")

app = create_app()
app.run()



