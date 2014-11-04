Changelog
=========

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
