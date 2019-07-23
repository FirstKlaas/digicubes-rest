Get single right by id
======================

.. http:get:: /rights/(int: right_id)

    Gets a right specified by its id.

    **Example Request**

    .. sourcecode:: http

        GET /rights/2 HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        X-Filter-Fields: id

    :reqheader X-Filter-Fields: Comma seperated list of field wich
        should be send back. If omitted, all fields
        are send back. If an invalid field is specified it will be
        ignored.

    :resheader Last-Modified: The date, where the ressource has been
        modified.

    :resheader ETag: An unique id for this ressource. The value will
        change, when the ressource gets modified.

    :statuscode 200: No error

    :statuscode 404: Right does not exist
