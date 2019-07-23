Clear user roles
================

Removes all roles from a user.

    **Example Request**

    .. sourcecode:: http

        DELETE /users/354/roles/ HTTP/1.1
        Host: digicubes.org

    :statuscode 200: All roles been sucessfully removed from the user.
    :statuscode 404: The user with the id ``uder_id`` does not exist.
