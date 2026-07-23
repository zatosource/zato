# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http import HTTPStatus
from logging import getLogger

# Django
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url

# Zato
from zato.admin.settings import LOGIN_REDIRECT_URL
from zato.common.webapp.auth.config import auth_config, AuthType
from zato.common.webapp.auth.entra import EntraAuthError, get_authorize_url, handle_callback
from zato.admin.web.forms.main import AuthenticationForm
from zato.admin.web.util import get_user_profile
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

@method_allowed('GET')
def index_redirect(req):
    return HttpResponseRedirect('/zato')

# ################################################################################################################################

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/index.html')

# ################################################################################################################################

def get_login_response(req, needs_post_form_data, has_errors, entra_error:'str'=''):

    form = AuthenticationForm(req.POST if needs_post_form_data else None)

    is_entra = auth_config.auth_type == AuthType.Entra

    return TemplateResponse(req, 'zato/login.html', {
        'form': form,
        'next': req.GET.get('next', ''),
        'has_errors': has_errors or form.errors,
        'entra_enabled': is_entra,
        'entra_error': entra_error,
    })

# ################################################################################################################################

def login(req):

    logger.info('Login request received')

    # By default, assume the credentials are invalid unless proved otherwise
    has_errors = True

    # If it is a GET request, we only return the form to display
    if req.method == 'GET':
        needs_post_form_data = False
        logger.info('Login request -> GET')

        # No data was POST-ed so there cannot be any errors yet
        has_errors = False

        # With Entra ID enabled, a GET may go straight to Microsoft - either because auto-login is on
        # or because the person clicked the Microsoft button. The auth=built-in query parameter
        # always keeps the plain form reachable so local accounts can log in too.
        if auth_config.auth_type == AuthType.Entra:

            requested_auth = req.GET.get('auth', '')
            wants_built_in = requested_auth == AuthType.Built_In
            wants_entra = requested_auth == AuthType.Entra

            needs_entra_redirect = auth_config.auto_login
            if wants_entra:
                needs_entra_redirect = True
            if wants_built_in:
                needs_entra_redirect = False

            if needs_entra_redirect:
                next_path = req.GET.get('next', '')
                authorize_url = get_authorize_url(req, next_path)

                logger.info('Redirecting to the Entra ID authorize URL')
                return HttpResponseRedirect(authorize_url)
    else:

        logger.info('Login request -> POST')

        # Get credentials from request
        username = req.POST['username']
        password = req.POST['password']

        logger.info('Login username -> `%s`', username)

        # Check if basic credentials are valid
        user = authenticate(username=username, password=password)

        # If they are ..
        if user is not None:

            # Log in the user to site because we need the Django user object
            django_login(req, user)

            logger.info('User password confirmed `%s`', username)

            # Make sure the redirect-to address is valid
            redirect_to = req.POST.get('next', '') or req.GET.get('next', '')
            if not is_safe_url(url=redirect_to, allowed_hosts=req.get_host()):
                redirect_to = resolve_url(LOGIN_REDIRECT_URL)

            # Set timezone from browser if not already set
            browser_timezone = req.POST.get('browser_timezone', '').strip()
            logger.info('Browser timezone received: %r for user %s', browser_timezone, username)
            if browser_timezone:
                user_profile = get_user_profile(req.user)
                logger.info('Current user_profile.timezone: %r for user %s', user_profile.timezone, username)
                if user_profile.timezone in (None, ''):
                    logger.info('Timezone is None or empty, setting to %s for user %s', browser_timezone, username)
                    user_profile.timezone = browser_timezone
                    user_profile.save()
                    logger.info('Timezone saved to database: %s for user %s', browser_timezone, username)
                else:
                    logger.info('Timezone already set to %r, not overwriting for user %s', user_profile.timezone, username)
            else:
                logger.info('No browser timezone received for user %s', username)

            # At this point we know that all the possible credentials are valid
            # so we can log the user in and redirect the person further.
            logger.info('User credentials are valid, redirecting `%s` to `%s`', username, redirect_to)
            return HttpResponseRedirect(redirect_to)

        else:
            logger.warning('User password validation error `%s`', username)
            needs_post_form_data = True

    # Here, we know that we need to return the form, either because it is a GET request
    # or because it was POST but credentials were invalid
    return get_login_response(req, needs_post_form_data, has_errors)

# ################################################################################################################################

@method_allowed('GET')
def login_callback(req:'any_') -> 'any_':

    logger.info('Login callback request received')

    # Complete the sign-in with the external identity provider ..
    try:
        next_path = handle_callback(req)
    except EntraAuthError as e:
        logger.warning('Entra ID login error -> `%s`', e.args[0])
        return get_login_response(req, False, False, entra_error=e.args[0])

    # .. make sure the redirect-to address is valid ..
    if not is_safe_url(url=next_path, allowed_hosts=req.get_host()):
        next_path = resolve_url(LOGIN_REDIRECT_URL)

    # .. and the person can go to the dashboard now.
    logger.info('Entra ID login completed, redirecting to `%s`', next_path)

    out = HttpResponseRedirect(next_path)
    return out

# ################################################################################################################################

@login_required
@method_allowed('GET')
def session_keepalive(req):
    req.session.modified = True
    return HttpResponse(status=HTTPStatus.NO_CONTENT)

# ################################################################################################################################

@method_allowed('GET')
def logout(req):
    django_logout(req)
    return index_redirect(req)

# ################################################################################################################################
