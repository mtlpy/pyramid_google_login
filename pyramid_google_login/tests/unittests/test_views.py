import unittest

import mock


@mock.patch('pyramid_google_login.views.exchange_token_from_code')
@mock.patch('pyramid_google_login.views.get_userinfo_from_token')
@mock.patch('pyramid_google_login.views.get_principal_from_userinfo')
@mock.patch('pyramid_google_login.views.decode_state')
@mock.patch('pyramid_google_login.views.remember')
class TestCallback(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.params = {
            'code': 'CODE1234',
            'state': 'STATE1234'
        }
        self.settings = {
            'security.google_login.client_id': 'CLIENTID',
            'security.google_login.client_secret': 'CLIENTSECRET',
        }
        self.request.registry.settings = self.settings

        self.request.route_url.return_value = '/test/url'

    def test_nominal(self, m_rem, m_dec_s, m_get_p, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid.httpexceptions import HTTPFound

        m_rem.return_value = [('Set-Cookie', 'auth_tkt=plop')]
        m_dec_s.return_value = {'url': ['/next/url']}

        resp = callback(self.request)

        m_exch_t.assert_called_once_with(self.request)
        m_get_u.assert_called_once_with(m_exch_t.return_value)
        m_get_p.assert_called_once_with(self.request, m_get_u.return_value)
        m_rem.assert_called_once_with(self.request,
                                      principal=m_get_p.return_value,
                                      max_age=24 * 3600)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, '/next/url')

        expected_header = ('Set-Cookie', 'auth_tkt=plop')
        self.assertIn(expected_header, resp.headerlist)

    def test_no_url(self, m_rem, m_dec_s, m_get_p, m_get_u, m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid.httpexceptions import HTTPFound

        m_rem.return_value = [('Set-Cookie', 'auth_tkt=plop')]
        m_dec_s.return_value = {}

        resp = callback(self.request)

        self.assertIsInstance(resp, HTTPFound)
        self.assertEqual(resp.location, '/')

    def test_oauth2_flow_error(self, m_rem, m_dec_s, m_get_p, m_get_u,
                               m_exch_t):
        from pyramid_google_login.views import callback
        from pyramid_google_login import AuthFailed

        from pyramid.httpexceptions import HTTPFound

        m_exch_t.side_effect = AuthFailed('TESTEXC')

        with self.assertRaises(HTTPFound) as test_exc:
            callback(self.request)

        self.request.route_url.assert_called_once_with(
            'auth_signin',
            _query={'message': 'Google Login failed (TESTEXC)'})

        self.assertEqual(test_exc.exception.location,
                         '/test/url')

    def test_unkown_error(self, m_rem, m_dec_s, m_get_p, m_get_u,
                          m_exch_t):
        from pyramid_google_login.views import callback

        from pyramid.httpexceptions import HTTPFound

        m_exch_t.side_effect = Exception('TESTEXC')

        with self.assertRaises(HTTPFound) as test_exc:
            callback(self.request)

        self.request.route_url.assert_called_once_with(
            'auth_signin',
            _query={'message': 'Google Login failed (unkown)'})

        self.assertEqual(test_exc.exception.location,
                         '/test/url')
