Clear roles
===========

Removes all roles from the right.

    **Example Request**

    .. sourcecode:: http

        DELETE /rights/42/roles/ HTTP/1.1
        Host: digicubes.org

    :statuscode 200: All roles been sucessfully removed from the user.
    :statuscode 404: The right with the id ``right_id`` does not exist.
