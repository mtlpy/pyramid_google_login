import unittest
from webtest import TestApp

# from pyramid import testing





class Test(unittest.TestCase):
    def get_config(self):
        from pyramid.config import Configurator
        # from pyramid.security import Allow
        # from pyramid.authorization import ACLAuthorizationPolicy

        config = Configurator()

        config.add_settings({
            'security.google_login.client_id': 'CLIENT_ID',
            'security.google_login.client_secret': 'CLIENT_SECRET',
        })

        import pyramid_google_login
        config.include(pyramid_google_login)
        return config

    def setUp(self):
        config = self.get_config()
        self.app = TestApp(config.make_wsgi_app())

    def test_signin(self):
        resp = self.app.get('/auth/signin',
                            status=200)
        expected = '''href="http://localhost/auth/signin_redirect"'''
        self.assertIn(expected, resp.body)

    def test_signin_redirect(self):
        resp = self.app.get('/auth/signin_redirect',
                            status=302)

        expected = ('https://accounts.google.com/o/oauth2/auth?'
                    'scope=email&state=&redirect_uri='
                    'http%3A%2F%2Flocalhost%2Fauth%2Foauth2callback&'
                    'response_type=code&client_id=CLIENT_ID')
        self.assertEqual(resp.location, expected)

    def test_callback_error(self):
        resp = self.app.get('/auth/oauth2callback', params={'error': 'ERROR'},
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Error+from+Google+%28ERROR%29%29')
        self.assertEqual(resp.location, expected)

    def test_logout(self):
        self.app.set_cookie('auth_tkt', 'whatever')
        resp = self.app.get('/auth/logout',
                            status=302)

        expected = 'http://localhost/auth/signin?message=Logged+out%21'
        self.assertEqual(resp.location, expected)

