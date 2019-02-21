# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.forms import AuthenticationForm as zzz
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url

# Zato
from zato.admin.settings import LOGIN_REDIRECT_URL
from zato.admin.zato_settings import is_totp_enabled
from zato.admin.web.forms.main import AuthenticationForm
from zato.admin.web.views import method_allowed

# ################################################################################################################################

@method_allowed('GET')
def index_redirect(req):
    return HttpResponseRedirect('/zato')

# ################################################################################################################################

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/index.html')

# ################################################################################################################################

def login(req):

    # If it is a GET request, we only return the form to display
    if req.method == 'GET':
        needs_post_form_data = False
    else:

        # Get credentials from request
        username = req.POST['username']
        password = req.POST['password']
        totp_code = req.POST.get('totp_code')

        # Check if basic credentials are valid
        user = authenticate(username=username, password=password)

        # If they are ..
        if user is not None:

            # If TOTP is enabled, make sure that it matches what is expected
            if is_totp_enabled:
                zzz

            # Make sure the redirect-to address is valid
            redirect_to = req.POST.get('next', '') or req.GET.get('next', '')
            if not is_safe_url(url=redirect_to, host=req.get_host()):
                redirect_to = resolve_url(LOGIN_REDIRECT_URL)

            # At this point we know that all the possible credentials are valid
            # so we can log the user in and redirect the person further.
            django_login(req, user)
            return HttpResponseRedirect(redirect_to)

        else:
            needs_post_form_data = True

    # Here, we know that we need to return the form, either because it is a GET request
    # or because it was POST but credentials were invalid
    return TemplateResponse(req, 'zato/login.html', {
        'form': AuthenticationForm(req.POST if needs_post_form_data else None),
        'next': req.GET.get('next', ''),
    })

# ################################################################################################################################

@method_allowed('GET')
def logout(req):
    django_logout(req)
    return index_redirect(req)

# ################################################################################################################################
