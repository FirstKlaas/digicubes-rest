Delete a right
==============

.. http:delete:: /right/42

    Deletes a right specified by its id in the database

    **Example Request**

    .. sourcecode:: http

        DELETE /right/42 HTTP/1.1
        Host: digicubes.org
        Accept: application/json

    :statuscode 200: No error

    :statuscode 404: Right does not exist
