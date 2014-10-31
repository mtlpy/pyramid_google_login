import urllib
import urlparse

import requests
from requests.exceptions import RequestException

from pyramid_google_login import SETTINGS_PREFIX
from pyramid_google_login import AuthFailed


GOOGLE_AUTHORIZE = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN = "https://accounts.google.com/o/oauth2/token"
GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v2/userinfo"


def encode_state(params):
    return urllib.urlencode(params)


def decode_state(state):
    return urlparse.parse_qs(state)


def build_authorize_url(request, state):
    client_id = request.registry.settings[SETTINGS_PREFIX + 'client_id']

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": request.route_url("auth_callback"),
        "scope": "email",
        "state": state,
    }
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
        oauth2_response = resp.json()
    except RequestException as err:
        raise AuthFailed("Failed to get token from Google (%s)" % err)

    try:
        access_token = oauth2_response['access_token']
    except KeyError:
        raise AuthFailed("No access_token in response from Google")

    return access_token


def get_userinfo_from_token(access_token):
    resp = requests.get(GOOGLE_USERINFO,
                        params={'access_token': access_token})
    resp.raise_for_status()
    return resp.json()


def get_principal_from_userinfo(request, userinfo):
    user_id_field = request.registry.settings.get(
        SETTINGS_PREFIX + 'user_id_field',
        'email')

    try:
        principal = userinfo[user_id_field]
    except:
        raise AuthFailed("Missing principal field from Google userinfo")

    return principal
