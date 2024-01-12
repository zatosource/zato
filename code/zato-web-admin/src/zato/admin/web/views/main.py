# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url

# PyOTP
import pyotp

# Zato
from zato.admin.settings import LOGIN_REDIRECT_URL
from zato.admin import zato_settings
from zato.admin.web.forms.main import AuthenticationForm
from zato.admin.web.util import get_user_profile
from zato.admin.web.views import method_allowed
from zato.common.crypto.api import CryptoManager

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
        'is_totp_enabled': zato_settings.is_totp_enabled,
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
        totp_code = req.POST.get('totp_code') or -1

        logger.info('Login username -> `%s`', username)

        # Check if basic credentials are valid
        user = authenticate(username=username, password=password)

        # If they are ..
        if user is not None:

            # Log in the user to site because we need the Django user object
            django_login(req, user)

            logger.info('User password confirmed `%s`', username)

            # If TOTP is enabled, make sure that it matches what is expected
            if zato_settings.is_totp_enabled:

                logger.info('TOTP is enabled')

                # At this point the user is logged in but we still do not have the person's profile
                # so we need to look it up ourselves instead of relying on req.zato.user_profile.
                user_profile = get_user_profile(req.user)

                # This is what we have configured for user
                user_totp_data = user_profile.get_totp_data()

                # TOTP is required but it is not set for user, we need to reject such a request
                if not user_totp_data.key:
                    logger.warning('No TOTP key for user `%s`', username)
                    return get_login_response(req, True, True)

                # Decrypt the key found in the user profile
                cm = CryptoManager(secret_key=zato_settings.zato_secret_key)
                user_totp_key_decrypted = cm.decrypt(user_totp_data.key)

                # Confirm that what user provided is what we expected
                totp = pyotp.TOTP(user_totp_key_decrypted)

                if not totp.verify(totp_code):
                    logger.warning('Invalid TOTP code received')
                    return get_login_response(req, True, True)

            # Make sure the redirect-to address is valid
            redirect_to = req.POST.get('next', '') or req.GET.get('next', '')
            if not is_safe_url(url=redirect_to, allowed_hosts=req.get_host()):
                redirect_to = resolve_url(LOGIN_REDIRECT_URL)

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
def logout(req):
    django_logout(req)
    return index_redirect(req)

# ################################################################################################################################
