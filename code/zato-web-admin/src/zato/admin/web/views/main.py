# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
from zato.admin.web.forms.main import AuthenticationForm
from zato.admin.web.util import get_user_profile
from zato.admin.web.views import method_allowed

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

def get_login_response(req, needs_post_form_data, has_errors):

    form = AuthenticationForm(req.POST if needs_post_form_data else None)

    return TemplateResponse(req, 'zato/login.html', {
        'form': form,
        'next': req.GET.get('next', ''),
        'has_errors': has_errors or form.errors
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

@login_required
@method_allowed('GET')
def session_keepalive(req):
    return HttpResponse(status=204)

# ################################################################################################################################

@method_allowed('GET')
def logout(req):
    django_logout(req)
    return index_redirect(req)

# ################################################################################################################################
