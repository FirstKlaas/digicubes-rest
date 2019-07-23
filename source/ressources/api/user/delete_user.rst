Delete a user
=============

.. http:delete:: /users/12

    Deletes an user specified by its id in the database

    **Example Request**

    .. sourcecode:: http

        DELETE /users/12 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, login, email

    :statuscode 200: No error

    :statuscode 404: User does not exist

