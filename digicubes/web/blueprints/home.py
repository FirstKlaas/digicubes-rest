from flask import Blueprint, render_template, request, current_app, abort
from digicubes.web.forms import LoginForm
from digicubes.web.util import digi_client

home = Blueprint('home', __name__)

@home.route('/')
def index():
    return render_template("root/base.jinja")

@home.route('/login', methods=['GET', 'POST'])
def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        token = digi_client.login(login, password)
        app = current_app
        login_manager =  app.digicubes_login_manager

        if login_manager is None:
            return abort(500)

        if token is None:
            return login_manager.unauthorized()

        return login_manager.successful_logged_in()

    return render_template("root/login.jinja", form=form)
