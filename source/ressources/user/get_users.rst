GET Users
=========

Description
-----------

Returns an array of user dicts, that match the criterias
of the request. It is possible to select only certain
user attributes to be added to the response.

Request
-------

.. code-block:: http

    GET /users HTTP/1.1
    x-hateoa: <true | false>
    x-filter-fields: <user_attributes_to_be_included>

Headers
-------

Per default ressouce links will be generated for each user. Maybe this
is not always needed, as it add a lot of additinoal data to the output.
Setting the header field :code:`x-hateoa` to :code:`false` prevents
the service from rendering any link.

The header field :code:`x-filter-fields` contains the attributes you want
to be read for each user in the result. The attributes are provided as
comma seperated string. An example would be: :code:`login,firstName,email`
If ommitted, all attributes attributes are included in the response.

Links
-----

Link information is generated for the the ressource itself :code:`self` as
well as for related ressources.

.. code-block:: json

    {"links": [
        {
            "rel": "self",
            "href": "http://127.0.0.1:5042/users/4",
            "action": "GET",
            "types": [
                "application/json"
            ]
        },
        {
            "rel": "self",
            "href": "http://127.0.0.1:5042/users/4",
            "action": "PUT",
            "types": [
                "application/json"
            ]
        },
        {
            "rel": "self",
            "href": "http://127.0.0.1:5042/users/4",
            "action": "DELETE",
            "types": []
        },
        {
            "rel": "users",
            "href": "http://127.0.0.1:5042/users/",
            "action": "GET",
            "types": [
                "application/json"
            ]
        },
        {
            "rel": "roles",
            "href": "http://127.0.0.1:5042/users/4/roles/",
            "action": "GET",
            "types": [
                "application/json"
            ]
        }
    ]}

