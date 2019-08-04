.. digicubes rest documentation master file, created by
   sphinx-quickstart on Sun Jul  7 21:36:39 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to digicubes REST API documentation
===========================================

.. image:: /_static/pylint-badge.svg
    :target: http://pylint.pycqa.org/en/latest/

.. image:: /_static/python_version.svg
    :target: https://www.python.org/

.. image:: /_static/style_black.svg
    :target: https://github.com/ambv/black

.. _CRUD: https://en.wikipedia.org/wiki/Create,_read,_update_and_delete

The DigiCubes offers a human friendly and easy to use REST API. It follows
standard `CRUD`_ pattern and uses
therefore the http methods ``POST``, ``GET``, ``PUT``, ``DELETE``.
After successful login, a bearer token is send back from the server which
has to be included in every following request. The tokens have a standard
lifetime of 30 minutes. But this is configurable. All clients must update
there token from time to time.

.. toctree::
   :maxdepth: 3

   getting_started
   installation
   authentification
   ressources
   models
   util_functions

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
