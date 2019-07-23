Delete all users
================

.. http:delete:: /users/

    Deletes all users in the database

    **Example Request**

    .. sourcecode:: http

        DELETE /users/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, login, email


    :statuscode 200: No error
