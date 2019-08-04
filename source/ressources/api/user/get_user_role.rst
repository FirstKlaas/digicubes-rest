Get a user role by id
=====================

.. http:get:: /users/(int:user_id)/roles/(int:role_id)

    Gets a user role. The user and the role are specified by their id.
    If either the user_id or the role_id cannot be found in the database,
    a response status of 404 is send back.

    **Example Request**

    .. sourcecode:: http

        GET /users/354/roles/3 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

    :reqheader Authorization: .. include:: ../headers/authorization.rst

    :reqheader X-Filter-Fields: .. include:: ../headers/x_filter_fields.rst

    :statuscode 200: No error. The response body contains the json
        encoded role. If ``X-Filter-Fields`` was set, only the
        specified attributes.

    :statuscode 404: .. include:: ../statuscodes/status_404.rst
