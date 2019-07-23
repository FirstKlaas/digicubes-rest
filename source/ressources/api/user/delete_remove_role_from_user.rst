Remove role from user
=====================

    **Example Request**

    .. sourcecode:: http

        DELETE /users/354/roles/3 HTTP/1.1
        Host: digicubes.org

    :statuscode 200: No error. The response body contains the json
        encoded user. If ``X-Filter-Fields`` was set, only the
        spcified attributes.

    :statuscode 404: There are several reasons for this Status.
        The user with the id ``uder_id`` does not exist. The
        role with the id ``role_id`` does not exist.

