# -*- coding: utf-8 -*-
import logging

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

    config.scan('pyramid_google_login')




