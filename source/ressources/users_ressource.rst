Users Ressource
===============

Create one or more user
-----------------------

.. http:post:: /users/

    Create new user or new users. If the body contains a dict,
    the method will try to create a single user. If the body
    contains a json list object, the method wil try to create
    multiple users in a bulk operation.

    The bulk creation is wrapped in a transaction. So, if the
    creation of one user fails, the whole operation fails and
    no user will be created.

    If a single user was created, the response body contains
    the generated user ressource. This also includes auto
    generated field values like the id.

    **Example Request for a single user**

    .. sourcecode:: http

        POST /users/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, created_at

        {
            "login" : "ratchet",
            "mail" : "ratchet@digicubes.org"
        }

    **Example Request for multiple users**

    .. sourcecode:: http

        POST /users/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json

        [
            {
                "login" : "ratchet",
                "mail" : "ratchet@digicubes.org"
            },
            {
                "login" : "clank",
                "mail" : "clank@digicubes.org"
            }
        ]

    :reqheader x-filter-field: The list of attributes that should be returned
        for the newly created ressource. If this header field is omitted, all
        fields are returned. This field is only supported, when creating a
        single ressource. For bulk creation this header field is ignored, because
        no data is returned.

    :statuscode 201: The operation was successfull and the user
        or the users have been created successfully.

    :statuscode 500: Body contains unsupported data.

    :statuscode 409: At least one model constraint was violated.

    :statuscode 400: An unexpected error occurred.

Get multiple users
------------------

.. http:get:: /users/

    Gets all users.

    **Example Request**

    .. sourcecode:: http

        GET /users/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, login, email

    :reqheader X-Filter-Fields: Comma seperated list of field wich
        should be send back for each user. If omitted, all Fields
        are send back. If an invalid field is specified it will be
        ignored.

    :statuscode 200: No error

Delete all users
----------------

.. http:delete:: /users/

    Deletes all users in the database

    **Example Request**

    .. sourcecode:: http

        DELETE /users/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, login, email


    :statuscode 200: No error
