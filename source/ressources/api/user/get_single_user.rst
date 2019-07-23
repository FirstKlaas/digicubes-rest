Get user by id
==============

.. http:get:: /users/(int: user_id)

    Gets a user specified by its id.

    **Example Request**

    .. sourcecode:: http

        GET /users/12 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, login, email

    :reqheader X-Filter-Fields: Comma seperated list of field wich
        should be send back. If omitted, all fields
        are send back. If an invalid field is specified it will be
        ignored.

    :resheader Last-Modified: The date, where the ressource has been
        modified.

    :resheader ETag: An unique id for this ressource. The value will
        change, when the ressource gets modified.

    :statuscode 200: No error

    :statuscode 404: User does not exist
