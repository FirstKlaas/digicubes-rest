from flask import Blueprint, render_template

home = Blueprint('home', __name__)

@home.route('/')
def index():
    return render_template("root/hello.jinja")

@home.route('/login')
def login():
    return "Hier login"
