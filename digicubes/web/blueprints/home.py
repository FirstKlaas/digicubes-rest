from flask import Blueprint, render_template, request
from digicubes.web.forms import LoginForm
from digicubes.web.util import digi_client

home = Blueprint('home', __name__)

@home.route('/')
def index():
    return render_template("root/hello.jinja")

@home.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        token = digi_client.login(login, password)
        return f"Well Done: { token }"

    return render_template("root/login.jinja", form=form)
