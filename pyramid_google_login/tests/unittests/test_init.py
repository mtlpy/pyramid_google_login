import unittest

import mock


class TestIncludeme(unittest.TestCase):

    def test_includeme(self):
        from pyramid_google_login import includeme

        config = mock.Mock()

        includeme(config)

        config.include.assert_called_once_with('pyramid_mako')
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
        config.scan.assert_called_once_with()


class TestHelpers(unittest.TestCase):

    def test_redirect_to_signin(self):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login import redirect_to_signin

        request = mock.Mock()

        httpfound = redirect_to_signin(request)
        self.assertIsInstance(httpfound, HTTPFound)

        request.route_url.assert_called_once_with('auth_signin', _query={})
        self.assertEqual(httpfound.location, request.route_url.return_value)

    def test_redirect_to_signin_url(self):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login import redirect_to_signin

        request = mock.Mock()

        httpfound = redirect_to_signin(request, url='/test')
        self.assertIsInstance(httpfound, HTTPFound)

        request.route_url.assert_called_once_with('auth_signin',
                                                  _query={'url': '/test'})
        self.assertEqual(httpfound.location, request.route_url.return_value)

    def test_redirect_to_signin_headers(self):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login import redirect_to_signin

        request = mock.Mock()

        test_header = ('X-Test', 'Yeap')

        httpfound = redirect_to_signin(request, headers=[test_header])
        self.assertIsInstance(httpfound, HTTPFound)

        self.assertEqual(httpfound.location, request.route_url.return_value)
        self.assertIn(test_header, httpfound.headerlist)

    def test_find_landing_path(self):
        from pyramid_google_login import find_landing_path

        request = mock.Mock()
        request.registry.settings = {

        }

        path = find_landing_path(request)

        self.assertEqual(path, '/')

    def test_find_landing_path_landing_url(self):
        from pyramid_google_login import find_landing_path

        request = mock.Mock()
        request.registry.settings = {
            'security.google_login.landing_url': '/foobar',
        }

        path = find_landing_path(request)

        self.assertEqual(path, '/foobar')

    def test_find_landing_path_landing_route(self):
        from pyramid_google_login import find_landing_path

        request = mock.Mock()
        request.registry.settings = {
            'security.google_login.landing_route': 'myroute',
        }

        path = find_landing_path(request)

        self.assertEqual(path, request.route_path.return_value)

    def test_find_landing_path_landing_route_static(self):
        from pyramid_google_login import find_landing_path

        request = mock.Mock()
        request.registry.settings = {
            'security.google_login.landing_route': 'myroute',
        }
        request.route_path.side_effect = KeyError()

        path = find_landing_path(request)

        self.assertEqual(path, request.static_path.return_value)

    def test_find_landing_path_fallback(self):
        from pyramid_google_login import find_landing_path

        request = mock.Mock()
        request.registry.settings = {
            'security.google_login.landing_route': 'myroute',
        }
        request.route_path.side_effect = KeyError()
        request.static_path.side_effect = KeyError()

        path = find_landing_path(request)

        self.assertEqual(path, '/')
