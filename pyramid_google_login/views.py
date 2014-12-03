import logging

from pyramid.view import view_config
# from pyramid.settings import asbool
from pyramid.security import (remember, forget, NO_PERMISSION_REQUIRED)
from pyramid.httpexceptions import HTTPFound

from pyramid_google_login import SETTINGS_PREFIX
from pyramid_google_login import redirect_to_signin, find_landing_path
from pyramid_google_login import AuthFailed
from pyramid_google_login.events import UserLoggedIn, UserLoggedOut
from pyramid_google_login.google_oauth2 import (build_authorize_url,
                                                exchange_token_from_code,
                                                get_userinfo_from_token,
                                                check_hosted_domain_user,
                                                get_user_id_from_userinfo,
                                                encode_state,
                                                decode_state,
                                                )

log = logging.getLogger(__name__)


def includeme(config):
    config.add_route('auth_signin', '/auth/signin')
    config.add_route('auth_signin_redirect', '/auth/signin_redirect')
    config.add_route('auth_callback', '/auth/oauth2callback')
    config.add_route('auth_logout', '/auth/logout')

    config.add_static_view('static/pyramid_google_login',
                           'pyramid_google_login:static',
                           cache_max_age=300)

    config.scan(__name__)


@view_config(route_name='auth_signin',
             permission=NO_PERMISSION_REQUIRED,
             renderer='pyramid_google_login:templates/signin.mako')
def signin(request):
    settings = request.registry.settings
    signin_banner = settings.get(SETTINGS_PREFIX + 'signin_banner')
    hosted_domain = settings.get(SETTINGS_PREFIX + 'hosted_domain')
    signin_advice = settings.get(SETTINGS_PREFIX + 'signin_advice')
    message = request.params.get('message')
    url = request.params.get('url')

    if request.authenticated_userid:
        if url:
            return HTTPFound(location=url)
        else:
            return HTTPFound(location=find_landing_path(request))

    if url:
        redirect_url = request.route_url('auth_signin_redirect',
                                         _query={'url': url})
    else:
        redirect_url = request.route_url('auth_signin_redirect')

    return {'signin_redirect_url': redirect_url,
            'message': message,
            'signin_banner': signin_banner,
            'signin_advice': signin_advice,
            'hosted_domain': hosted_domain,
            }


@view_config(route_name='auth_signin_redirect',
             permission=NO_PERMISSION_REQUIRED,)
def signin_redirect(request):
    state_params = {}
    if 'url' in request.params:
        state_params['url'] = request.params['url']

    state = encode_state(state_params)
    try:
        redirect_uri = build_authorize_url(request, state)
    except AuthFailed as err:
        log.warning("Google Login failed (%s)", err)
        return redirect_to_signin(request, "Google Login failed (%s)" % err)

    return HTTPFound(location=redirect_uri)


@view_config(route_name='auth_callback',
             permission=NO_PERMISSION_REQUIRED)
def callback(request):
    try:
        oauth2_token = exchange_token_from_code(request)
        userinfo = get_userinfo_from_token(oauth2_token)
        check_hosted_domain_user(request, userinfo)
        userid = get_user_id_from_userinfo(request, userinfo)

    except AuthFailed as err:
        log.warning("Google Login failed (%s)", err)
        return redirect_to_signin(request, "Google Login failed (%s)" % err)

    except Exception as err:
        log.warning("Google Login failed (%s)", err)
        # Protect against leaking critical information like client_secret
        return redirect_to_signin(request, "Google Login failed (unkown)")

    # Find the redirect url (fail-safe, the authentication is more important)
    try:
        state_params = decode_state(request.params['state'])
        url = state_params['url'][0]
    except:
        url = find_landing_path(request)

    user_logged_in = UserLoggedIn(request, userid, oauth2_token, userinfo)
    try:
        request.registry.notify(user_logged_in)
    except:
        log.exception("Application crashed processing UserLoggedIn event"
                      "\nuserinfo=%s oauth2_token=%s",
                      userinfo, oauth2_token)
        return redirect_to_signin(request,
                                  "Google Login failed (application error)")

    if user_logged_in.headers:
        headers = user_logged_in.headers
    else:
        headers = remember(request, principal=userid)
    return HTTPFound(location=url, headers=headers)


@view_config(route_name='auth_logout')
def logout(request):
    userid = request.unauthenticated_userid
    if userid is not None:
        event = UserLoggedOut(userid)
        request.registry.notify(event)

    headers = forget(request)
    return redirect_to_signin(request, "You are logged out!", headers=headers)
