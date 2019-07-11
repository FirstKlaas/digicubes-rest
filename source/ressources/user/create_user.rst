CREATE User
===========

Description
-----------

Creates a new user ressource. The body of the post request must contain
a valid dictionary describing the new user. Only the updatable values
of a user are used. Any additional value in the body of the request will
be ignored.

If the request was successful, a status of 201 will be send back.
The newly created ressource will be send back json formatted in
the body of the response. The returning dict contains all automatically
generated values. The `Location` header field contains the URL for the
newly created ressource.

A status of 409 will be send back if a model constraint has been violated.
An example would be to create a new user with a non unique login.

A status of 400 will be send back, if the request was maformed.

Request
-------

.. code-block:: http

    POST /users HTTP/1.1
    x-hateoa: <true | false>
    x-filter-fields: <user_attributes_to_be_included>

Sample body for a new user:

.. code-block:: json

    {
        "login"     : "firstklaas",
        "firstName" : "Klaas",
        "lastName"  : "Nebuhr"
    }

Headers
-------

