Get multiple users
==================

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
