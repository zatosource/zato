# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.urls import path
from django.views.generic.base import RedirectView

# Zato
from zato.common.webapp.static import static_file
from zato.openapi.app.views import branding_view, favicon_view, login_view, logo_view, logout_view, portal_view, \
    relay_view, spec_view, spec_yaml_view

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', RedirectView.as_view(url='/api-portal', permanent=False)),
    path('api-portal', portal_view, name='portal'),
    path('api-portal/login', login_view, name='login'),
    path('api-portal/logout', logout_view, name='logout'),
    path('api-portal/openapi.json', spec_view, name='spec'),
    path('api-portal/openapi.yaml', spec_yaml_view, name='spec-yaml'),
    path('api-portal/relay', relay_view, name='relay'),
    path('api-portal/branding/logo', logo_view, name='logo'),
    path('api-portal/branding/<str:file_name>', branding_view, name='branding'),
    path('static/<path:path>', static_file, name='static'),
    path('favicon.ico', favicon_view, name='favicon'),
]

# ################################################################################################################################
# ################################################################################################################################
