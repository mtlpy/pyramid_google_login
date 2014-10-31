import logging

from pyramid.view import view_config
from pyramid.security import (remember, forget, NO_PERMISSION_REQUIRED)
from pyramid.httpexceptions import HTTPFound

from pyramid_google_login import SETTINGS_PREFIX
from pyramid_google_login.google_oauth2 import (build_authorize_url,
                                                exchange_token_from_code,
                                                get_userinfo_from_token,
                                                encode_state,
                                                decode_state,
                                                )

log = logging.getLogger(__name__)


@view_config(route_name='auth_signin',
             permission=NO_PERMISSION_REQUIRED,
             renderer='pyramid_google_login:templates/signin.mako')
def signin(context, request):
    settings = request.registry.settings
    signin_banner = settings.get(SETTINGS_PREFIX + 'signin_banner')

    signin_advice = settings.get(SETTINGS_PREFIX + 'signin_advice',
                                 'Please sign in with your Google account')
    message = request.params.get('message', signin_advice)

    if 'url' in request.params:
        url = request.route_url("auth_signin_redirect",
                                _query={'url': request.params['url']})
    else:
        url = request.route_url("auth_signin_redirect")

    return {'signin_redirect_url': url,
            'message': message,
            'signin_banner': signin_banner
            }


@view_config(route_name='auth_signin_redirect',
             permission=NO_PERMISSION_REQUIRED,)
def signin_redirect(context, request):
    state_params = {}
    if 'url' in request.params:
        state_params['url'] = request.params['url']

    state = encode_state(state_params)
    redirect_uri = build_authorize_url(request, state)

    return HTTPFound(location=redirect_uri)


@view_config(route_name='auth_callback',
             permission=NO_PERMISSION_REQUIRED)
def callback(context, request):
    settings = request.registry.settings
    user_id_field = settings.get(SETTINGS_PREFIX + 'user_id_field', 'email')
    landing_url = settings.get(SETTINGS_PREFIX + 'landing_url', '/')
    max_age = int(settings.get(SETTINGS_PREFIX + 'max_age', 24 * 3600))

    try:
        access_token = exchange_token_from_code(request)
        userinfo = get_userinfo_from_token(access_token)
        principal = userinfo[user_id_field]
    except Exception as err:
        error_msg = "Google Login failed (%s)" % err
        log.warning(error_msg)
        url = request.route_url('auth_signin', _query={'message': error_msg})
        return HTTPFound(location=url)

    # Find the redirect url (fail-safe, the authentication is more important)
    try:
        state_params = decode_state(request.params['state'])
        url = state_params['url'][0]
    except:
        url = landing_url

    headers = remember(request, principal=principal, max_age=max_age)
    return HTTPFound(location=url, headers=headers)


@view_config(route_name='auth_logout')
def logout(context, request):
    url = request.route_url('auth_signin', _query={'message': "Logged out!"})

    headers = forget(request)

    return HTTPFound(location=url, headers=headers)
