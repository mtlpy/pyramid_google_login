# -*- coding: utf-8 -*-
import logging

from pyramid.httpexceptions import HTTPFound

log = logging.getLogger(__name__)


SETTINGS_PREFIX = 'security.google_login.'


def includeme(config):
    log.info("Add pyramid_google_login")

    config.include('pyramid_mako')
    config.include('.utility')
    config.include('.views')


def redirect_to_signin(request, message=None, url=None, headers=None):
    """ Redirect to the sign in page with message and next url """
    query = {}
    if message is not None:
        query['message'] = message
    if url is not None:
        query['url'] = url
    url = request.route_url('auth_signin', _query=query)
    return HTTPFound(location=url, headers=headers)


def find_landing_path(request):
    settings = request.registry.settings

    landing_url = settings.get(SETTINGS_PREFIX + 'landing_url')
    if landing_url is not None:
        return landing_url

    landing_route = settings.get(SETTINGS_PREFIX + 'landing_route')
    if landing_route is not None:
        try:
            return request.route_path(landing_route)
        except KeyError:
            pass
        try:
            return request.static_path(landing_route)
        except KeyError:
            pass

    return '/'
