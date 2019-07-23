Update an existing user
=======================

.. http:put:: /user/(int: user_id)

    Update an existing user. The body of the request must
    contain a json dict with the attributes you want to
    update.

    Only *writable* attributes of the user entity can be
    updated. Attributes of the json object which
    represent readonly or non-existent fields are ignored.

    The updated user will be returned in the response
    body.

    The request supports the ``X-Filter-Field`` header entry.

    **Example Request**

    .. sourcecode:: http

        PUT /users/2 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, created_at

        {
            "login" : "ratchet",
            "mail" : "ratchet@digicubes.org",
            "id" : 33,
            "size" : "XL"
        }

    In this example the two attributes ``id`` and ``size``
    would be ignored. The former, because it is a read-only
    field, the latter, because the user entity has no such
    attribute.

    :<json string login: The users login name
    :<json string email: The users email
    :<json string firstName: The users first name
    :<json string lastName: The users last name
    :<json boolean is_activated: Flag, is the user is activated
    :<json boolean is_verified: Flag, if the users email was verified

    :reqheader x-filter-field: The list of attributes that should be returned
        for the updated ressource. If this header field is omitted, all
        fields are returned.

    :statuscode 200: The operation was successfull and the user
        is returned in the body.

    :statuscode 500: An unexpected error occurred.

    :statuscode 404: The user does not exist.
