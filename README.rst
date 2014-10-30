====================
Pyramid_google_login
====================

Google Login extention for Pyramid. Implement the OAuth2 Server-side flow.


* PyPI: https://pypi.python.org/pypi/pyramid_google_login
* Bitbucket: https://bitbucket.org/Ludia/pyramid_google_login
* Bugs: https://bitbucket.org/Ludia/pyramid_google_login/issues


Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ pip install pyramid_google_login


Setup
=====

Settings from paster configuration::

   security.google_login.client_id = xxxxxxx.apps.googleusercontent.com
   security.google_login.client_secret = xxxxxxxxxxxxxxxxxxxxxxxxx
   # security.google_login.user_id_field = email
   # security.google_login.landing_url = /
   # security.google_login.max_age = 86400


Usage
=====

Once ``pyramid_google_login`` is installed, you must use the ``config.include``
mechanism to include it into your Pyramid project's configuration.  In your
Pyramid project's ``__init__.py``:

.. code-block:: python

   config = Configurator(.....)
   config.include('pyramid_google_login')

Alternately you can use the ``pyramid.includes`` configuration value in your
``.ini`` file:

.. code-block:: ini

   [app:myapp]
   pyramid.includes = pyramid_google_login


Development
===========

Running tests::

   $ virtualenv venv
   $ . venv/bin/activate
   (venv)$ pip install -r requirements-test.txt
   (venv)$ nosetests
