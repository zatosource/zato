# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.urls import path
from django.views.generic.base import RedirectView

# Zato
from zato.openapi.app.views import branding_view, console_view, login_callback_view, login_view, logout_view, relay_view, \
    spec_view, spec_yaml_view, static_view

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', RedirectView.as_view(url='/openapi/console', permanent=False)),
    path('openapi/console', console_view, name='console'),
    path('openapi/console/login', login_view, name='login'),
    path('openapi/console/login/callback', login_callback_view, name='login-callback'),
    path('openapi/console/logout', logout_view, name='logout'),
    path('openapi/console/openapi.json', spec_view, name='spec'),
    path('openapi/console/openapi.yaml', spec_yaml_view, name='spec-yaml'),
    path('openapi/console/relay/<path:relay_path>', relay_view, name='relay'),
    path('openapi/console/branding/<str:file_name>', branding_view, name='branding'),
    path('static/<path:file_path>', static_view, name='static'),
]

# ################################################################################################################################
# ################################################################################################################################
