# -*- coding: utf-8 -*-
import logging

from pyramid.httpexceptions import HTTPFound

log = logging.getLogger(__name__)


SETTINGS_PREFIX = 'security.google_login.'


class AuthFailed(Exception):
    pass


def includeme(config):
    log.info("Add pyramid_google_login")

    config.include('pyramid_mako')

    config.add_route('auth_signin', '/auth/signin')
    config.add_route('auth_signin_redirect', '/auth/signin_redirect')
    config.add_route('auth_callback', '/auth/oauth2callback')
    config.add_route('auth_logout', '/auth/logout')

    config.add_static_view('static', 'pyramid_google_login:static')

    config.scan()


def redirect_to_signin(request, message=None, url=None, headers=None):
    """ Redirect to the sign in page with message and next url """
    query = {}
    if message is not None:
        query['message'] = message
    if url is not None:
        query['url'] = url
    url = request.route_url('auth_signin', _query=query)
    raise HTTPFound(location=url, headers=headers)
