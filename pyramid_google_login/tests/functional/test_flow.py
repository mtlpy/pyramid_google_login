from . import Base


class Test(Base):

    def test_signin(self):
        resp = self.app.get('/auth/signin',
                            status=200)
        expected = '''href="http://localhost/auth/signin_redirect"'''
        self.assertIn(expected, resp.body)

    def test_signin_url(self):
        resp = self.app.get('/auth/signin?url=TESTURL',
                            status=200)
        expected = ('''href="http://localhost/auth/signin_redirect'''
                    '''?url=TESTURL"''')
        self.assertIn(expected, resp.body)

    def test_signin_message(self):
        resp = self.app.get('/auth/signin?message=TEST+MESSAGE',
                            status=200)
        expected = '''TEST MESSAGE'''
        self.assertIn(expected, resp.body)

    def test_signin_redirect(self):
        resp = self.app.get('/auth/signin_redirect?url=TEST%2FURL',
                            status=302)

        expected = (
            'https://accounts.google.com/o/oauth2/auth?'
            'access_type=offline&state=url%3DTEST%252FURL&'
            'redirect_uri=http%3A%2F%2Flocalhost%2Fauth%2Foauth2callback&'
            'response_type=code&client_id=client+id&scope=email&hd=bob.com')
        self.assertEqual(resp.location, expected)

    def test_callback_error(self):
        resp = self.app.get('/auth/oauth2callback',
                            params={'error': 'ERROR'},
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28Error+from+Google+%28ERROR%29%29')
        self.assertEqual(resp.location, expected)

    def test_callback_no_code(self):
        resp = self.app.get('/auth/oauth2callback',
                            status=302)

        expected = ('http://localhost/auth/signin?message='
                    'Google+Login+failed+%28No+authorization+code+from'
                    '+Google%29')
        self.assertEqual(resp.location, expected)

    def test_logout(self):
        self.app.set_cookie('auth_tkt', 'whatever')
        resp = self.app.get('/auth/logout',
                            status=302)

        expected = 'http://localhost/auth/signin?message=You+are+logged+out%21'
        self.assertEqual(resp.location, expected)
