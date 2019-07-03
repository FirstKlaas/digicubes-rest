import json

from digicubes.storage.models import User

from .. import Blueprint

user = Blueprint('/user')

@user.route('/')
def user_index(req, resp):
    resp.text = repr(req)

@user.route('/id/{id}')
async def get_user(req, resp, *, id):
    user = await User.filter(id=id).first()
    resp.json = user

@user.route('/login/{login}')
async def get_user_by_login(req, resp, *, login):
    print(f" ----> Headers: {req.headers.get('dicicubes-fields',None)}")

    user = await User.filter(login=login).first()
    if user is not None:
        d = user.as_dict(['login', 'id', 'created_at'])
        resp.media = d
    else:
        resp.text = "not found"