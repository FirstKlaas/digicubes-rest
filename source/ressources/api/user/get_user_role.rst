Get a user role by id
=====================

.. http:get:: /users/(int:userid)/roles/(int:role_id)

    Gets a user role.

    The user and the role are specified by their id.

    **Example Request**

    .. sourcecode:: http

        GET /users/354/roles/3 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

    .. include:: ../headers/authorization.rst

    .. include:: ../headers/x_filter_fields.rst

    :statuscode 200: No error. The response body contains the json
        encoded role. If ``X-Filter-Fields`` was set, only the
        specified attributes.

    .. include:: ../statuscodes/status_404.rst
