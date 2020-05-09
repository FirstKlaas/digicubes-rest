import responder

from digicubes_rest.storage import models


def add_item_routes(api: responder.API):
    @api.route("/school/byname/{data}")
    async def get_school_by_name(req: responder.Request, resp: responder.Response, *, data):
        # pylint: disable=unused-variable
        if req.method == "get":
            school = await models.School.get_or_none(name=data)
            if school is None:
                resp.status_code = 404
                resp.text = f"School with name {data} not found."
            else:
                resp.media = school.unstructure()
        else:
            resp.status_code = 405
            resp.text = "Method not allowed"

    @api.route("/user/bylogin/{data}")
    async def get_user_by_login(req: responder.Request, resp: responder.Response, *, data):
        # pylint: disable=unused-variable
        if req.method == "get":
            user = await models.User.get_or_none(login=data)
            if user is None:
                resp.status_code = 404
                resp.text = f"User with login {data} not found."
            else:
                resp.media = user.unstructure(exclude_fields=["password_hash"])
        else:
            resp.status_code = 405
            resp.text = "Method not allowed"

    @api.route("/school/{school_id}/teacher")
    async def get_school_teacher(req: responder.Request, resp: responder.Response, *, school_id):
        # pylint: disable=unused-variable
        async def on_get():
            school = await models.School.get_or_none(id=school_id)
            if school is None:
                resp.status_code = 404
                resp.text = f"School with id {school_id} not found."
            else:
                teacher = await school.teacher.all()
                resp.media = [t.unstructure(exclude_fields=["password_hash"]) for t in teacher]

        if req.method == "get":
            await on_get()
        else:
            resp.status_code = 405
            resp.text = "Method not allowed"
