# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.urls import path

# Zato
from zato.common.webapp.static import static_file
from zato.openapi.app.views import branding_view, favicon_view, login_view, logo_view, logout_view, portal_view, \
    relay_view, spec_view, spec_yaml_view

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', portal_view, name='portal'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('openapi.json', spec_view, name='spec'),
    path('openapi.yaml', spec_yaml_view, name='spec-yaml'),
    path('relay', relay_view, name='relay'),
    path('branding/logo', logo_view, name='logo'),
    path('branding/<str:file_name>', branding_view, name='branding'),
    path('static/<path:path>', static_file, name='static'),
    path('favicon.ico', favicon_view, name='favicon'),
]

# ################################################################################################################################
# ################################################################################################################################
