import unittest
from webtest import TestApp


class Test(unittest.TestCase):
    def set_config(self, settings=None):
        if settings is None:
            settings = {
                'security.google_login.client_id': 'CLIENT_ID',
                'security.google_login.client_secret': 'CLIENT_SECRET',
                'security.google_login.access_type': 'offline',
            }

        from pyramid.config import Configurator
        config = Configurator()
        config.add_settings(settings)

        import pyramid_google_login
        config.include(pyramid_google_login)

        self.app = TestApp(config.make_wsgi_app())

    def test_signin(self):
        self.set_config()
        resp = self.app.get('/auth/signin',
                            status=200)
        expected = '''href="http://localhost/auth/signin_redirect"'''
        self.assertIn(expected, resp.body)

    def test_signin_url(self):
        self.set_config()
        resp = self.app.get('/auth/signin?url=TESTURL',
                            status=200)
        expected = ('''href="http://localhost/auth/signin_redirect'''
                    '''?url=TESTURL"''')
        self.assertIn(expected, resp.body)

    def test_signin_message(self):
        self.set_config()
        resp = self.app.get('/auth/signin?message=TEST+MESSAGE',
                            status=200)
        expected = '''TEST MESSAGE'''
        self.assertIn(expected, resp.body)

    def test_signin_redirect(self):
        self.set_config()
        resp = self.app.get('/auth/signin_redirect?url=TEST%2FURL',
                            status=302)

        expected = (
            'https://accounts.google.com/o/oauth2/auth?'
            'access_type=offline&state=url%3DTEST%252FURL&'
            'redirect_uri=http%3A%2F%2Flocalhost%2Fauth%2Foauth2callback&'
            'response_type=code&client_id=CLIENT_ID&scope=email')
        self.assertEqual(resp.location, expected)

    def test_signin_redirect_missing_clientid(self):
        self.set_config({})

        resp = self.app.get('/auth/signin_redirect',
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Missing+settings%29')
        self.assertEqual(resp.location, expected)

    def test_callback_error(self):
        self.set_config()
        resp = self.app.get('/auth/oauth2callback',
                            params={'error': 'ERROR'},
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Error+from+Google+%28ERROR%29%29')
        self.assertEqual(resp.location, expected)

    def test_callback_no_code(self):
        self.set_config()
        resp = self.app.get('/auth/oauth2callback',
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28No+authorization+code+from'
                    '+Google%29')
        self.assertEqual(resp.location, expected)

    def test_callback_missing_clientid(self):
        self.set_config({})
        resp = self.app.get('/auth/oauth2callback',
                            params={'code': 'TESTCODE'},
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Missing+settings%29')
        self.assertEqual(resp.location, expected)

    def test_callback_missing_clientsecret(self):
        self.set_config({
            'security.google_login.client_id': 'CLIENT_ID',
        })
        resp = self.app.get('/auth/oauth2callback',
                            params={'code': 'TESTCODE'},
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Missing+settings%29')
        self.assertEqual(resp.location, expected)

    def test_logout(self):
        self.set_config()
        self.app.set_cookie('auth_tkt', 'whatever')
        resp = self.app.get('/auth/logout',
                            status=302)

        expected = 'http://localhost/auth/signin?message=You+are+logged+out%21'
        self.assertEqual(resp.location, expected)
