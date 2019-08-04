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

    .. include:: ../authorization_header_field.rst

    .. include:: ../x_filter_fields_header_field.rst

    :statuscode 200: No error. The response body contains the json
        encoded user. If ``X-Filter-Fields`` was set, only the
        spcified attributes.

    :statuscode 404: There are several reasons for this Status.
        The user with the id ``uder_id`` does not exist. The
        role with the id ``role_id`` does not exist. The role
        does exist, but is not associated with this user.

