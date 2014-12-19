import unittest
import urlparse

import mock


class TestState(unittest.TestCase):

    def test_encode_state(self):
        from pyramid_google_login.google_oauth2 import encode_state

        tested = [('param1', 'value1'),
                  ('param2', 'value2'),
                  ('param2', 'value3')]
        resp = encode_state(tested)
        expected = 'param1=value1&param2=value2&param2=value3'
        self.assertEqual(resp, expected)

    def test_decode_state(self):
        from pyramid_google_login.google_oauth2 import decode_state

        tested = 'param1=value1&param2=value2&param2=value3'
        resp = decode_state(tested)
        expected = {'param1': ['value1'], 'param2': ['value2', 'value3']}
        self.assertEqual(resp, expected)


class TestBuildAuthorizeUrl(unittest.TestCase):

    def test_nominal(self):
        from pyramid_google_login.google_oauth2 import build_authorize_url

        request = mock.Mock()
        request.route_url.return_value = 'TESTROUTEURL'
        request.registry.settings = {
            'security.google_login.client_id': 'CLIENTID',
            'security.google_login.hosted_domain': 'example.net',
            'security.google_login.access_type': 'offline',
            'security.google_login.scopes': """
                https://www.googleapis.com/auth/admin.directory.user.readonly
                """,
        }
        state = 'TESTSTATE'

        url = build_authorize_url(request, state)
        expected = (
            'https://accounts.google.com/o/oauth2/auth?'
            'access_type=offline&'
            'state=TESTSTATE&'
            'redirect_uri=TESTROUTEURL&'
            'response_type=code&'
            'client_id=CLIENTID&'
            'scope=email+https%3A%2F%2Fwww.googleapis.com%2F'
            'auth%2Fadmin.directory.user.readonly&'
            'hd=example.net')

        self.assertEqual(url, expected)

    def run_build_authorize_url_with_settings(self, settings):
        from pyramid_google_login.google_oauth2 import build_authorize_url

        request = mock.Mock()
        request.route_url.return_value = 'TESTROUTEURL'
        request.registry.settings = {
            'security.google_login.client_id': 'CLIENTID',
        }
        request.registry.settings.update(settings)

        url = build_authorize_url(request, '')
        return urlparse.parse_qs(urlparse.urlparse(url).query)

    def test_setting_access_type(self):
        settings = {}
        qs = self.run_build_authorize_url_with_settings(settings)
        self.assertIn('access_type', qs)
        self.assertEqual(qs['access_type'], ['online'])

        settings = {'security.google_login.access_type': 'online'}
        qs = self.run_build_authorize_url_with_settings(settings)
        self.assertIn('access_type', qs)
        self.assertEqual(qs['access_type'], ['online'])

        settings = {'security.google_login.access_type': 'offline'}
        qs = self.run_build_authorize_url_with_settings(settings)
        self.assertIn('access_type', qs)
        self.assertEqual(qs['access_type'], ['offline'])

    def test_setting_hosted_domain(self):
        settings = {}
        qs = self.run_build_authorize_url_with_settings(settings)
        self.assertNotIn('hd', qs)

        settings = {'security.google_login.hosted_domain': 'thing.example'}
        qs = self.run_build_authorize_url_with_settings(settings)
        self.assertIn('hd', qs)
        self.assertEqual(qs['hd'], ['thing.example'])

    def test_missing_setting(self):
        from pyramid_google_login.google_oauth2 import build_authorize_url
        from pyramid_google_login import AuthFailed

        request = mock.Mock()
        request.route_url.return_value = 'TESTROUTEURL'
        request.registry.settings = {}
        state = 'TESTSTATE'

        with self.assertRaises(AuthFailed) as test_exc:
            build_authorize_url(request, state)

        auth_failed = test_exc.exception
        self.assertEqual(auth_failed.message, 'Missing settings')


class TestExchangeTokenFromCode(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.params = {'code': 'CODE1234'}
        self.settings = {
            'security.google_login.client_id': 'CLIENTID',
            'security.google_login.client_secret': 'CLIENTSECRET',
        }
        self.request.registry.settings = self.settings

    def call_and_assert_raises_with_message(self, message):
        from pyramid_google_login import AuthFailed
        from pyramid_google_login.google_oauth2 import exchange_token_from_code

        with self.assertRaises(AuthFailed) as test_exc:
            exchange_token_from_code(self.request)

        self.assertEqual(test_exc.exception.message, message)

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_nominal(self, m_requests):
        from pyramid_google_login.google_oauth2 import exchange_token_from_code

        test_tokens = {
            'access_token': 'POIPOI',
            'refresh_token': 'REFRESH_POIPOI',
        }
        m_requests.post.return_value.json.return_value = test_tokens

        oauth2_tokens = exchange_token_from_code(self.request)

        self.assertEqual(oauth2_tokens, test_tokens)

    def test_param_error(self):
        self.request.params = {'error': 'TESTERROR'}
        self.call_and_assert_raises_with_message(
            'Error from Google (TESTERROR)')

    def test_param_no_code(self):
        self.request.params = {}
        self.call_and_assert_raises_with_message(
            'No authorization code from Google')

    def test_missing_client_id(self):
        del self.settings['security.google_login.client_id']
        self.call_and_assert_raises_with_message(
            'Missing settings')

    def test_missing_client_secret(self):
        del self.settings['security.google_login.client_secret']
        self.call_and_assert_raises_with_message(
            'Missing settings')

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_token_endpoint_request_error(self, m_requests):
        from requests.exceptions import RequestException

        m_requests.post.side_effect = RequestException('TESTEXC')

        self.call_and_assert_raises_with_message(
            'Failed to get token from Google (TESTEXC)')

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_token_endpoint_unknown_error(self, m_requests):
        m_requests.post.side_effect = Exception('TESTEXC')

        self.call_and_assert_raises_with_message(
            'Failed to get token from Google (unkown error)')

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_invalid_token_endpoint_response(self, m_requests):
        m_requests.post.return_value.json.return_value = {}

        self.call_and_assert_raises_with_message(
            'No access_token in response from Google')


class TestGetUserinfoFromToken(unittest.TestCase):

    def call_and_assert_raises_with_message(self, message):
        from pyramid_google_login import AuthFailed
        from pyramid_google_login.google_oauth2 import get_userinfo_from_token

        test_tokens = {
            'access_token': 'POIPOI',
            'refresh_token': 'REFRESH_POIPOI',
        }

        with self.assertRaises(AuthFailed) as test_exc:
            get_userinfo_from_token(test_tokens)

        self.assertEqual(test_exc.exception.message, message)

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_nominal(self, m_requests):
        from pyramid_google_login.google_oauth2 import get_userinfo_from_token

        m_json_response = m_requests.get.return_value.json.return_value

        test_tokens = {
            'access_token': 'POIPOI',
            'refresh_token': 'REFRESH_POIPOI',
        }

        userinfo = get_userinfo_from_token(test_tokens)

        self.assertEqual(userinfo, m_json_response)

    @mock.patch('pyramid_google_login.google_oauth2.requests')
    def test_userinfo_endpoint_unknown_error(self, m_requests):
        m_requests.get.side_effect = Exception('TESTEXC')

        self.call_and_assert_raises_with_message(
            'Failed to get userinfo from Google')


class TestCheckHostedDomainUser(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.params = {'code': 'CODE1234'}
        self.settings = {
            'security.google_login.hosted_domain': 'example.net',
        }
        self.request.registry.settings = self.settings

    def test_nominal(self):
        from pyramid_google_login.google_oauth2 import (
            check_hosted_domain_user)

        userinfo = {'hd': 'example.net'}
        check_hosted_domain_user(self.request, userinfo)

    def test_wrong_domain(self):
        from pyramid_google_login import AuthFailed
        from pyramid_google_login.google_oauth2 import (
            check_hosted_domain_user)

        userinfo = {'hd': 'reallynotexample.net'}

        with self.assertRaises(AuthFailed) as test_exc:
            check_hosted_domain_user(self.request, userinfo)

        self.assertEqual(test_exc.exception.message,
                         'You logged in with an unkown domain '
                         '(reallynotexample.net rather than example.net)')

    def test_missing_userinfo_field(self):
        from pyramid_google_login import AuthFailed
        from pyramid_google_login.google_oauth2 import (
            check_hosted_domain_user)

        userinfo = {}

        with self.assertRaises(AuthFailed) as test_exc:
            check_hosted_domain_user(self.request, userinfo)

        self.assertEqual(test_exc.exception.message,
                         'Missing hd field from Google userinfo')


class TestGetPrincipalFromUserinfo(unittest.TestCase):
    def test_nominal(self):
        from pyramid_google_login.google_oauth2 import (
            get_user_id_from_userinfo)

        userinfo = {'email': 'TESTEMAIL', 'id': 'TESTID'}

        request = mock.Mock()

        request.registry.settings = {}
        principal = get_user_id_from_userinfo(request, userinfo)
        self.assertEqual(principal, 'TESTEMAIL')

        request.registry.settings = {
            'security.google_login.user_id_field': 'email'}
        principal = get_user_id_from_userinfo(request, userinfo)
        self.assertEqual(principal, 'TESTEMAIL')

        request.registry.settings = {
            'security.google_login.user_id_field': 'id'}
        principal = get_user_id_from_userinfo(request, userinfo)
        self.assertEqual(principal, 'TESTID')

    def test_missing_field(self):
        from pyramid_google_login import AuthFailed
        from pyramid_google_login.google_oauth2 import (
            get_user_id_from_userinfo)

        userinfo = {}

        request = mock.Mock()
        request.registry.settings = {}

        with self.assertRaises(AuthFailed) as test_exc:
            get_user_id_from_userinfo(request, userinfo)

        self.assertEqual(test_exc.exception.message,
                         'Missing user id field from Google userinfo')
