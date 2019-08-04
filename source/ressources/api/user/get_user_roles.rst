Get user roles
==============

.. http:get:: /users/12/roles/

    Get all roles for a user. If the request was successfull, a json array
    containing the roles is send back in the response body.

    **Example Request**:

    .. sourcecode:: http

        GET /users/12/roles HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: application/json
        Content-Length: 116

        [
            {
                "name": "root",
                "id": 1,
                "created_at": "2019-08-04T11:45:30.287238",
                "modified_at": "2019-08-04T11:45:30.287240"
            }
        ]


    :reqheader Authorization: .. include:: ../headers/authorization.rst

    :reqheader X-Filter-Fields: .. include:: ../headers/x_filter_fields.rst

    :statuscode 200: No error. The response body contains the json
        encoded user. If ``X-Filter-Fields`` was set, only the
        specified attributes.

    :statuscode 404: .. include:: ../statuscodes/status_404.rst

