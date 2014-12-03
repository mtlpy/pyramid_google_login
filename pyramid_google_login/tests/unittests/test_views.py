import unittest

from pyramid import testing
import mock


class TestIncludeme(unittest.TestCase):

    def test_includeme(self):
        from pyramid_google_login.views import includeme

        config = mock.Mock()

        includeme(config)

        expected_calls = [
            mock.call('auth_signin', '/auth/signin'),
            mock.call('auth_signin_redirect', '/auth/signin_redirect'),
            mock.call('auth_callback', '/auth/oauth2callback'),
            mock.call('auth_logout', '/auth/logout'),
        ]
        config.add_route.assert_has_calls(expected_calls, any_order=True)
        config.add_static_view.assert_called_once_with(
            'static/pyramid_google_login',
            'pyramid_google_login:static',
            cache_max_age=300)
        config.scan.assert_called_once_with('pyramid_google_login.views')


@mock.patch('pyramid_google_login.views.exchange_token_from_code')
@mock.patch('pyramid_google_login.views.get_userinfo_from_token')
@mock.patch('pyramid_google_login.views.get_user_id_from_userinfo')
@mock.patch('pyramid_google_login.views.decode_state')
@mock.patch('pyramid_google_login.views.remember')
class TestCallback(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.params = {
            'code': 'CODE1234',
            'state': 'STATE1234'
        }
        self.settings = {
            'security.google_login.client_id': 'CLIENTID',
            'security.google_login.client_secret': 'CLIENTSECRET',
        }

        testing.setUp(settings=self.settings)
        #self.request.route_url.return_value = '/test/url'

    def tearDown(self):
        testing.tearDown()

    def test_nominal(self, m_rem, m_dec_s, m_get_uid, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid.httpexceptions import HTTPFound

        m_rem.return_value = [('Set-Cookie', 'auth_tkt=plop')]
        m_dec_s.return_value = {'url': ['/next/url']}

        resp = callback(self.request)

        m_exch_t.assert_called_once_with(self.request)
        m_get_u.assert_called_once_with(m_exch_t.return_value)
        m_get_uid.assert_called_once_with(self.request, m_get_u.return_value)
        m_rem.assert_called_once_with(self.request,
                                      principal=m_get_uid.return_value)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, '/next/url')

        expected_header = ('Set-Cookie', 'auth_tkt=plop')
        self.assertIn(expected_header, resp.headerlist)

    def test_event(self, m_rem, m_dec_s, m_get_uid, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid_google_login.events import UserLoggedIn

        subscriber = mock.Mock()

        with testing.testConfig() as config:
            config.add_subscriber(subscriber, UserLoggedIn)
            callback(self.request)

        subscriber.assert_called_once_with(mock.ANY)

        event = subscriber.call_args[0][0]

        self.assertEqual(event.userid, m_get_uid.return_value)
        self.assertEqual(event.oauth2_token, m_exch_t.return_value)
        self.assertEqual(event.userinfo, m_get_u.return_value)

    def test_event_error(self, m_rem, m_dec_s, m_get_uid, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login.events import UserLoggedIn

        subscriber = mock.Mock()
        subscriber.side_effect = Exception()

        with testing.testConfig() as config:
            config.add_subscriber(subscriber, UserLoggedIn)
            config.add_route('auth_signin', '/test/url')
            resp = callback(self.request)

        self.assertIsInstance(resp, HTTPFound)

        self.assertEqual(
            resp.location,
            'http://example.com/test/url?message='
            'Google+Login+failed+%28application+error%29',
            )

    def test_no_url(self, m_rem, m_dec_s, m_get_uid, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid.httpexceptions import HTTPFound

        m_rem.return_value = [('Set-Cookie', 'auth_tkt=plop')]
        m_dec_s.return_value = {}

        resp = callback(self.request)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, '/')

    def test_oauth2_flow_error(self, m_rem, m_dec_s, m_get_uid, m_get_u,
                               m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid_google_login import AuthFailed

        from pyramid.httpexceptions import HTTPFound

        m_exch_t.side_effect = AuthFailed('TESTEXC')

        with testing.testConfig() as config:
            config.add_route('auth_signin', '/test/url')
            test_exc = callback(self.request)

        self.assertIsInstance(test_exc, HTTPFound)

        self.assertEqual(
            test_exc.location,
            'http://example.com/test/url?message='
            'Google+Login+failed+%28TESTEXC%29',
            )

    def test_unkown_error(self, m_rem, m_dec_s, m_get_uid, m_get_u,
                          m_exch_t):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login.views import callback

        m_exch_t.side_effect = Exception('TESTEXC')

        with testing.testConfig() as config:
            config.add_route('auth_signin', '/test/url')
            test_exc = callback(self.request)

        self.assertIsInstance(test_exc, HTTPFound)

        self.assertEqual(
            test_exc.exception.location,
            'http://example.com/test/url?message='
            'Google+Login+failed+%28unkown%29',
            )

    def test_custom_cookie(self, m_rem, m_dec_s, m_get_uid, m_get_u,
                           m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid_google_login.events import UserLoggedIn

        m_dec_s.return_value = {'url': ['/next/url']}

        def subscriber(event):
            event.headers = [('Set-Cookie', 'user=bob')]

        with testing.testConfig() as config:
            config.add_subscriber(subscriber, UserLoggedIn)
            response = callback(self.request)

        self.assertIn('Set-Cookie', response.headers)
        self.assertEqual('user=bob', response.headers.get('Set-Cookie'))


@mock.patch('pyramid_google_login.views.find_landing_path')
class TestSignin(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.params = {
        }
        self.settings = {
            'security.google_login.signin_banner': 'CLIENTID',
            'security.google_login.client_secret': 'CLIENTSECRET',
        }
        self.request.registry.settings = self.settings

        self.request.authenticated_userid = None
        self.request.route_url.return_value = '/test/url'

    def test_nominal(self, m_find_landing_path):
        from pyramid_google_login.views import signin
        # from pyramid.httpexceptions import HTTPFound

        resp = signin(self.request)

        expected = {'hosted_domain': None,
                    'message': None,
                    'signin_advice': None,
                    'signin_banner': 'CLIENTID',
                    'signin_redirect_url': '/test/url'}

        self.assertEqual(resp, expected)

    def test_authenticated(self, m_find_landing_path):
        from pyramid_google_login.views import signin
        from pyramid.httpexceptions import HTTPFound

        self.request.authenticated_userid = '123'

        resp = signin(self.request)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, m_find_landing_path.return_value)

    def test_authenticated_with_url(self, m_find_landing_path):
        from pyramid_google_login.views import signin
        from pyramid.httpexceptions import HTTPFound

        self.request.params['url'] = '/go/there'
        self.request.authenticated_userid = '123'

        resp = signin(self.request)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, '/go/there')


@mock.patch('pyramid_google_login.views.redirect_to_signin')
class TestLogout(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.settings = {}
        self.request.registry.settings = self.settings

    def test_nominal(self, m_redirect):
        from pyramid_google_login.views import logout
        from pyramid_google_login.events import UserLoggedOut, Event

        resp = logout(self.request)

        self.assertEqual(resp, m_redirect.return_value)

        self.assertEqual(self.request.registry.notify.called, True)
        event = self.request.registry.notify.call_args[0][0]

        self.assertIsInstance(event, UserLoggedOut)
        self.assertIsInstance(event, Event)
        self.assertEqual(event.userid, self.request.unauthenticated_userid)
