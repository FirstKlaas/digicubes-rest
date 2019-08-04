Login
=====

.. http:post:: /users/login/

    Login to DigiCubes and get yout bearer token.

    **Example Request**

    .. sourcecode:: http

        POST /users/login/ HTTP/1.1
        Host: digicubes.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
            "bearer_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE1NjQ5Mzk1MjksImlhdCI6MTU2NDkzNzcyOX0.Pc__JWfMEQd99PItfqC46cmxFg3BiuGh2EL8uecF5Kg",
            "user_id": 1
        }

    :statuscode 200: No error. The response body contains the bearer
        token to be used in subsequent requests.

    :statuscode 401: .. include:: ../statuscodes/status_404.rst
