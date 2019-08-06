Login
=====

.. http:post:: /users/token/

    Updates the token. The bearer token used for authentification has a certain
    *lifetime* and will expire. Using an expired token will result in a
    ``401 - Unauthorized`` response. So be shure to update the token before
    it gets expired.

    **Example Request**

    .. sourcecode:: http

        POST /users/login/ HTTP/1.1
        Host: digicubes.org
        Authorizaton: Bearer <token>
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

    :statuscode 404: .. include:: ../statuscodes/status_404.rst

    :statuscode 401: The user is not authorized. This happens, if the provided
        token is wrong or expired.
