DELETE User
===========

Description
-----------

Deletes a single user. All related ressources are deleted as well.
This operation can not be undone. So be carefull

Request
-------

.. code-block:: http

    DELETE /users/<id> HTTP/1.1

`<id>` is the id of the user to be updated.

Headers
-------

No special headers are required
