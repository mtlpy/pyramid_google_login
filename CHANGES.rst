Changelog
=========

1.0.3 (2015-02-20)
------------------

* Add ``request.googleapi_settings`` containing google api specific settings.
  It's created at configuration time to fail early when some info is missing.
* Add ``request.googleapi`` created and reified for each request. It
  encapsulates google api functionalities.
* Move ``AuthFailed`` to ``pyramid_google_login.exceptions``
* Add event ``AccessTokenExpired`` to be notified by client to refresh
  automatically access_token.

1.0.2 (2014-12-19)
------------------

* Fix incorrect authorize url format for multiple scopes

1.0.1 (2014-12-03)
------------------

* ``UserLoggedIn.headers`` permit subscribers to add headers to be returned in
  response and set customised auth cookie rather than default email.
* Add a setting for the access_type. Default to ``online``

1.0.0 (2014-11-26)
------------------

* Change internal API to get access to all OAuth2 tokens from view
* Change authorization request for offline credentials (to get a refresh_token)
* Add options to specify the OAuth2 scopes
* Send Pyramid events ``UserLoggedIn`` and ``UserLoggedOut``
* Removed setting ``max_age`` (should be set in AuthTktAuthenticationPolicy)

0.5.0 (2014-11-06)
------------------

* Fix issue with config.scan() (pyramid/venusian importing tests)

0.4.0 (2014-11-06)
------------------

0.3.0 (2014-11-06)
------------------

* Resolve landing path from settings landing_url and landing_route
* Redirect authenticated user to landing page from sign in page

0.2.0 (2014-11-04)
------------------

* Change redirect_to_signin to return HTTPFound (rather than raising it)

0.1.2 (2014-11-04)
------------------

0.1.1 (2014-11-04)
------------------

0.1.0 (2014-11-04)
------------------

* Initial setup
* Naive implementation of the server-side Google authentication flow
* Add a stylish sign in page
* Add a public helper function pyramid_google_login.redirect_to_signin
* Change error reporting during OAuth2 second phase to avoid leaking secrets
* Add protection against unkown error in oauth2 functions
* Add tests
* Add option to limit login to one Google Hosted Domain
