"""
The Admin Blueprint
"""
from flask import Blueprint, render_template

from digicubes.web.util import digi_client, login_required

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
def index():
    return render_template("root/base.jinja")

@admin.route('/users/')
def user_list():
    return render_template("root/user_list.jinja")
