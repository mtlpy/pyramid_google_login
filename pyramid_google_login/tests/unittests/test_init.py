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

        with self.assertRaises(HTTPFound) as test_exc:
            redirect_to_signin(request)

        request.route_url.assert_called_once_with('auth_signin', _query={})
        httpfound = test_exc.exception
        self.assertEqual(httpfound.location, request.route_url.return_value)

    def test_redirect_to_signin_url(self):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login import redirect_to_signin

        request = mock.Mock()

        with self.assertRaises(HTTPFound) as test_exc:
            redirect_to_signin(request, url='/test')

        request.route_url.assert_called_once_with('auth_signin',
                                                  _query={'url': '/test'})
        httpfound = test_exc.exception
        self.assertEqual(httpfound.location, request.route_url.return_value)

    def test_redirect_to_signin_headers(self):
        from pyramid.httpexceptions import HTTPFound
        from pyramid_google_login import redirect_to_signin

        request = mock.Mock()

        test_header = ('X-Test', 'Yeap')

        with self.assertRaises(HTTPFound) as test_exc:
            redirect_to_signin(request, headers=[test_header])

        httpfound = test_exc.exception
        self.assertEqual(httpfound.location, request.route_url.return_value)
        self.assertIn(test_header, httpfound.headerlist)
