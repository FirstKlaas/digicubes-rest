Remove role from right
======================

    **Example Request**

    .. sourcecode:: http

        DELETE /rights/47/roles/3 HTTP/1.1
        Host: digicubes.org

    :statuscode 200: No error. The response body contains the json
        encoded role. If ``X-Filter-Fields`` was set, only the
        spcified attributes.

    :statuscode 404: There are several reasons for this Status.
        The role with the id ``role_id`` does not exist. The
        right with the id ``right_id`` does not exist.
