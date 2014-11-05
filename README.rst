====================
Pyramid Google Login
====================

Google Login extension for Pyramid. Implement the OAuth2 Server-side flow.

This extension doesn't configure any authentication policy. You are responsible
of setting the proper security configuration in your Pyramid application. When
authenticated by Google, this extension calls the method
``pyramid.security.remember`` and assume the authentication policy will
remember the user identity.

* PyPI: https://pypi.python.org/pypi/pyramid_google_login
* Bitbucket: https://bitbucket.org/Ludia/pyramid_google_login
* Tests: |droneio|
* Bugs: https://bitbucket.org/Ludia/pyramid_google_login/issues

.. |droneio| image::
   https://drone.io/bitbucket.org/Ludia/pyramid_google_login/status.png
   :target: https://drone.io/bitbucket.org/Ludia/pyramid_google_login
   :alt: Tests on drone.io


Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ pip install pyramid_google_login


Setup: Application
==================

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

Settings::

   security.google_login.client_id = xxxxxxx.apps.googleusercontent.com
   security.google_login.client_secret = xxxxxxxxxxxxxxxxxxxxxxxxx
   # security.google_login.user_id_field = email
   # security.google_login.hosted_domain = example.net
   # security.google_login.landing_url = /
   # security.google_login.landing_route = my_frontend_route
   # security.google_login.landing_route = mymodule:static/
   # security.google_login.max_age = 86400
   # security.google_login.signin_banner = Welcome on Project Euler


Setup: Google project
=====================

- Create a project on https://console.developers.google.com
- Create a OAuth Client ID

   + Choose a ``Web Application`` application type
   + Add all variants of your host in Javascript Origins

      * Secure and non secure url are differentiated
      * Optionally include your development host with
        ``http://localhost:6543`` rather than an ``http://127.0.0.1:6543``
        (it would be refused)

Notes:

- No ``Permissions`` are needed by ``pyramid_google_login`` itself.
- Client ID parameters are heavily cached. In development, re-creating a client
  id is often the best idea.


Usage
=====

When a user must be authenticated by Google, he must be sent to the
``auth_signin`` route url. The helper method
``pyramid_google_login.redirect_to_signin`` redirect a user to the sign in
page. This helper is handy to specify the next url and an optional message.

.. code-block:: python

   @forbidden_view_config()
   def unauthenticated(context, request):
       return redirect_to_signin(request, url=request.path_qs)

Once authenticated, the user will be redirected to an url specified by:

- query parameter (signin page): ``url``
- setting: ``security.google_login.landing_url``
- fallback: ``/``

When a user must be logged out, he must be directed on the ``auth_logout``
route url. Once logged out, he will be redirected back to the sign in page.


Development
===========

Running tests::

   $ virtualenv venv
   $ . venv/bin/activate
   (venv)$ pip install -r requirements-test.txt
   (venv)$ nosetests
