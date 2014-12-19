import logging
import urllib
import urlparse

import requests
from requests.exceptions import RequestException
from pyramid.settings import aslist

from pyramid_google_login import SETTINGS_PREFIX
from pyramid_google_login import AuthFailed

log = logging.getLogger(__name__)


GOOGLE_AUTHORIZE = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN = "https://accounts.google.com/o/oauth2/token"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v2/userinfo"


def encode_state(params):
    return urllib.urlencode(params)


def decode_state(state):
    return urlparse.parse_qs(state)


def build_authorize_url(request, state):
    settings = request.registry.settings
    hosted_domain = settings.get(SETTINGS_PREFIX + 'hosted_domain')
    access_type = settings.get(SETTINGS_PREFIX + 'access_type', 'online')

    scope_list = set(aslist(settings.get(SETTINGS_PREFIX + 'scopes', '')))
    scope_list.add('email')

    try:
        client_id = settings[SETTINGS_PREFIX + 'client_id']
    except:
        raise AuthFailed("Missing settings")

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": request.route_url("auth_callback"),
        "scope": ' '.join(scope_list),
        "state": state,
        "access_type": access_type,
    }

    if hosted_domain is not None:
        params['hd'] = hosted_domain

    authorize_url = "%s?%s" % (GOOGLE_AUTHORIZE, urllib.urlencode(params))

    return authorize_url


def exchange_token_from_code(request):
    if 'error' in request.params:
        raise AuthFailed("Error from Google (%s)" % request.params['error'])

    try:
        code = request.params['code']
    except KeyError as err:
        raise AuthFailed("No authorization code from Google")

    settings = request.registry.settings
    try:
        client_id = settings[SETTINGS_PREFIX + 'client_id']
        client_secret = settings[SETTINGS_PREFIX + 'client_secret']
    except KeyError as err:
        raise AuthFailed("Missing settings")

    params = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": request.route_url("auth_callback"),
        "grant_type": "authorization_code",
    }

    try:
        resp = requests.post(GOOGLE_TOKEN, data=params)
        resp.raise_for_status()
        oauth2_tokens = resp.json()
    except RequestException as err:
        raise AuthFailed("Failed to get token from Google (%s)" % err)
    except Exception as err:
        log.warning("Unkown error while calling token endpoint",
                    exc_info=True)
        raise AuthFailed("Failed to get token from Google (unkown error)")

    if 'access_token' not in oauth2_tokens:
        raise AuthFailed("No access_token in response from Google")

    return oauth2_tokens


def get_userinfo_from_token(oauth2_tokens):
    try:
        params = {'access_token': oauth2_tokens['access_token']}
        resp = requests.get(GOOGLE_USERINFO, params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        log.warning("Unkown error calling userinfo endpoint",
                    exc_info=True)
        raise AuthFailed("Failed to get userinfo from Google")


def check_hosted_domain_user(request, userinfo):
    settings = request.registry.settings
    hosted_domain = settings.get(SETTINGS_PREFIX + 'hosted_domain')

    if hosted_domain is None:
        return

    try:
        user_hosted_domain = userinfo['hd']
    except KeyError:
        raise AuthFailed("Missing hd field from Google userinfo")

    if hosted_domain != user_hosted_domain:
        raise AuthFailed("You logged in with an unkown domain "
                         "(%s rather than %s)" % (user_hosted_domain,
                                                  hosted_domain))


def get_user_id_from_userinfo(request, userinfo):
    user_id_field = request.registry.settings.get(
        SETTINGS_PREFIX + 'user_id_field',
        'email')

    try:
        user_id = userinfo[user_id_field]
    except:
        raise AuthFailed("Missing user id field from Google userinfo")

    return user_id
