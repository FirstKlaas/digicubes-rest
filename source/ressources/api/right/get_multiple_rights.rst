Get multiple rights
===================

.. http:get:: /rights/

    Gets all rights.

    **Example Request**

    .. sourcecode:: http

        GET /rights/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id, name

    :reqheader X-Filter-Fields: Comma seperated list of field wich
        should be send back for each right. If omitted, all Fields
        are send back. If an invalid field is specified it will be
        ignored.

    :statuscode 200: No error
