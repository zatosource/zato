# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url

# Zato
from zato.common.webapp.auth.config import auth_config, AuthType
from zato.common.webapp.auth.entra import EntraAuthError, get_authorize_url, handle_callback
from zato.rule_engine_dashboard.app.views.common import default_screen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _get_login_response(req:'any_', entra_error:'str'='') -> 'any_':
    """ Renders the sign-in form, keeping the post-login path across form round trips.
    """
    # The path travels in the form on POST and in the query string on GET
    if next_path := req.POST.get('next', ''):
        pass
    else:
        next_path = req.GET.get('next', '')

    is_entra = auth_config.auth_type == AuthType.Entra

    context = {
        'next': next_path,
        'entra_enabled': is_entra,
        'entra_error': entra_error,
    }

    out = render(req, 'login.html', context)
    return out

# ################################################################################################################################

def _handle_login_get(req:'any_') -> 'any_':
    """ A GET on the sign-in screen - either the form or a redirect to the identity provider.
    """

    # With the identity provider enabled, a GET may go straight there - either because auto-login
    # is on or because the person clicked the provider's button. The auth=built-in query parameter
    # always keeps the plain form reachable so local accounts can sign in too.
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

            out = HttpResponseRedirect(authorize_url)
            return out

    out = _get_login_response(req)
    return out

# ################################################################################################################################

def _handle_login_post(req:'any_') -> 'any_':
    """ A POST on the sign-in screen - the local credentials check.
    """
    username = req.POST.get('username', '')
    password = req.POST.get('password', '')

    # Django's own authentication decides - it also refuses disabled accounts ..
    user = authenticate(username=username, password=password)

    # .. wrong credentials render the form again with a message ..
    if user is None:
        logger.warning('Sign-in error for username `%s`', username)
        messages.error(req, 'Invalid username or password')

        out = _get_login_response(req)
        return out

    # .. and correct ones start the session.
    django_login(req, user)

    logger.info('User `%s` signed in', username)

    # The person goes back to where they were headed, if that path is safe to follow
    redirect_to = req.POST.get('next', '')
    is_safe = is_safe_url(url=redirect_to, allowed_hosts={req.get_host()})

    if not is_safe:
        redirect_to = default_screen(user)

    out = HttpResponseRedirect(redirect_to)
    return out

# ################################################################################################################################

def login(req:'any_') -> 'any_':
    """ The sign-in screen - a local form plus the identity provider when one is configured.
    """
    if req.method == 'GET':
        out = _handle_login_get(req)

    elif req.method == 'POST':
        out = _handle_login_post(req)

    # .. anything else is not a method this screen serves.
    else:
        out = HttpResponseNotAllowed(['GET', 'POST'])

    return out

# ################################################################################################################################

def login_callback(req:'any_') -> 'any_':
    """ Completes a sign-in with the identity provider - the user is provisioned
    in this application's own database and the session starts.
    """
    if req.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    # The provider's response may report an error, which goes back onto the sign-in form ..
    try:
        next_path = handle_callback(req)
    except EntraAuthError as e:
        logger.warning('Entra ID sign-in error -> `%s`', e.args[0])

        out = _get_login_response(req, entra_error=e.args[0])
        return out

    # .. the post-login path must be safe to follow ..
    if not is_safe_url(url=next_path, allowed_hosts={req.get_host()}):
        next_path = default_screen(req.user)

    # .. and the person is signed in now.
    out = HttpResponseRedirect(next_path)
    return out

# ################################################################################################################################

def logout(req:'any_') -> 'any_':
    """ Ends the session and returns to the sign-in screen.
    """
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    django_logout(req)

    out = redirect('login')
    return out

# ################################################################################################################################
# ################################################################################################################################
