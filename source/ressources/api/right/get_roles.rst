Get roles for a right
=====================

.. http:get:: /rights/2/roles/

    Get all roles, ascociated with the specified right. The right is
    specified by its id.

    The requesting user needs to have root rights or the right:
    ``GET_USER_ROLES``.

    **Example Request**

    .. sourcecode:: http

        GET /rights/2/roles/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json
        Authorizaton: Bearer <token>
        X-Filter-Fields: id, name

    :reqheader Authorization: .. include:: ../headers/authorization.rst

    :reqheader X-Filter-Fields: .. include:: ../headers/x_filter_fields.rst

    :statuscode 200: The body contains a list of jsonified roles.

    :statuscode 404: .. include:: ../statuscodes/status_404.rst

