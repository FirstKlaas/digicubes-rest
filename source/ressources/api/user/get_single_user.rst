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
        Authorization: Bearer <token>

        Where '<token>' should be replaced by the token you got from
        the login request.

    .. include:: ../headers/authorization.rst

    .. include:: ../headers/x_filter_fields.rst

    :resheader Last-Modified: The date, where the ressource has been
        modified.

    :resheader ETag: An unique id for this ressource. The value will
        change, when the ressource gets modified.

    :statuscode 200: No error. The response body contains the json
        encoded user. If ``X-Filter-Fields`` was set, only the
        specified attributes.

    .. include:: ../statuscodes/status_404.rst
