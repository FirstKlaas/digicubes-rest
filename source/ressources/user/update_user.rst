UPDATE User
===========

Description
-----------

Updates an existing user. The body of the post request must contain
a valid dictionary describing the new user. Only the updatable values
of a user are used. Any additional value in the body of the request will
be ignored.

If the request was successful, a status of 200 will be send back.
The response body contains the json formatted user.

Response status
---------------

+-----+-----------------------------------------------------------+
| 200 | User was successfully updated.                            |
+-----+-----------------------------------------------------------+
| 400 | The request was malformed. Error is send back.            |
+-----+-----------------------------------------------------------+
| 404 | The user with given id was not found.                     |
+-----+-----------------------------------------------------------+
| 409 | A model constraint was violated. Error is send back.      |
+-----+-----------------------------------------------------------+

Request
-------

.. code-block:: http

    POST /users/<id> HTTP/1.1
    x-hateoa: <true | false>

`<id>` is the id of the user to be updated.

Sample body for a new user:

.. code-block:: json

    {
        "login"     : "firstklaas",
        "firstName" : "Klaas",
        "lastName"  : "Nebuhr"
    }

Headers
-------
