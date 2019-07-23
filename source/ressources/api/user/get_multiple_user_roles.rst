Get multiple user roles
=======================

    **Example Request**

    .. sourcecode:: http

        GET /users/354/roles/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json

    :statuscode 200: No error. The response body contains the json
        array containing the user roles. If ``X-Filter-Fields`` was
        set, only the specified attributes are send back..

    :statuscode 404: The user with the id ``uder_id`` does not exist.

