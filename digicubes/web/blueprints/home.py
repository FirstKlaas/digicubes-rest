from flask import Blueprint, render_template, g

from digicubes.web.flask import login_required

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def index():
    client = g.digicubes_client
    token = client.login("root", "digicubes")
    #print(client.user.all())
    return render_template("root/hello.jinja", token=token, users=client.user.all())
