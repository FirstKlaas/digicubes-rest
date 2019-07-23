Delete multiple rights
======================

.. http:delete:: /rights/

    Delete multiple rights. For the time being, it deletes all
    rights, as we do not support any filters.

    **Example Request**

    .. sourcecode:: http

        GET /rights/42 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name, email

    :statuscode 200: No error
