.. digicubes rest documentation master file, created by
   sphinx-quickstart on Sun Jul  7 21:36:39 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to digicubes REST documentation
=======================================

.. autoclass:: digicubes.server.ressource.RightRoleRoute

    .. automethod:: on_get(req, resp, *, right_id, role_id)
    .. automethod:: on_put(req, resp, *, right_id, role_id)
    .. automethod:: on_delete(req, resp, *, right_id, role_id)

.. toctree::
   :maxdepth: 2

   introduction
   getting_started
   ressources

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
