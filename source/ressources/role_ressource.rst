Role Ressource
==============

Operations for a specific role. The role is specified
by its database id. The method ``POST`` is not allowed
and will return a status ``405 Method not allowed``.

Update an existing role
-----------------------

.. http:put:: /user/(int: user_id)

    Update an existing role. The body of the request must
    contain a json dict with the attributes you want to
    update.

    Only *writable* attributes of the role entity can be
    updated. Attributes of the json object which
    represent readonly or non-existent fields are ignored.

    The updated role will be returned in the response
    body.

    The request supports the ``X-Filter-Field`` header entry.

    **Example Request**

    .. sourcecode:: http

        PUT /role/2 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

        {
            "name" : "admin",
            "id" : 33,
            "size" : "XL"
        }

    In this example the two attributes ``id`` and ``size``
    would be ignored. The former, because it is a read-only
    field, the latter, because the role entity has no such
    attribute.

    :<json string name: The role name

    :reqheader x-filter-field: The list of attributes that should be returned
        for the updated ressource. If this header field is omitted, all
        fields are returned.

    :statuscode 200: The operation was successfull and the role
        is returned in the body.

    :statuscode 500: An unexpected error occurred.

    :statuscode 404: The role does not exist.
