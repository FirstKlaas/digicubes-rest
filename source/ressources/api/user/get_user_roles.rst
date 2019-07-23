Get user roles
==============

.. http:get:: /users/12/roles/

    Get all roles for a user. If the request was successfull, a json array
    containing the roles is send back in the response body.

    **Example Request**

    .. sourcecode:: http

        GET /users/12/roles HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

    :statuscode 200: No error

    :statuscode 404: User does not exist

