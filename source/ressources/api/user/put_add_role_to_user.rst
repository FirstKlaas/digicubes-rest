Add a role to a user
====================

**Example Request**

    .. sourcecode:: http

        PUT /users/354/roles/3 HTTP/1.1
        Host: digicubes.org
        Accept: application/json

    :statuscode 200: Role was added successfully
    :statuscode 404: There are several reasons for this Status.
        The user with the id ``user_id`` does not exist. The
        role with the id ``role_id`` does not exist.
