Create one or more rights
=========================

.. http:post:: /rights/

    Create new right or new rights. If the body contains a dict,
    the method will try to create a single right. If the body
    contains a json list object, the method wil try to create
    multiple rights in a bulk operation.

    The bulk creation is wrapped in a transaction. So, if the
    creation of one right fails, the whole operation fails and
    no user will be created.

    If a single right was created, the response body contains
    the generated right ressource. This also includes auto
    generated field values like the id.

    **Example Request for a single user**

    .. sourcecode:: http

        POST /rights/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, created_at

        {
            "name" : "DELETE_USER",
        }

    **Example Request for multiple users**

    .. sourcecode:: http

        POST /rights/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json

        [
            {
                "name" : "DELETE_USER"
            },
            {
                "name" : "DEACTIVATE_USER",
            }
        ]

    :reqheader x-filter-field: The list of attributes that should be returned
        for the newly created ressource. If this header field is omitted, all
        fields are returned. This field is only supported, when creating a
        single ressource. For bulk creation this header field is ignored, because
        no data is returned.

    :statuscode 201: The operation was successfull and the right
        or the rights have been created successfully.

    :statuscode 500: Body contains unsupported data.

    :statuscode 409: At least one model constraint was violated.

    :statuscode 400: An unexpected error occurred.
