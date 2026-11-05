# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path

# Zato
from zato.common.b2b.portal.views import asset_view, empty_view, home_view, logo_view, section_view

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', home_view, name='home'),
    path('assets/<path:path>', asset_view, name='asset'),
    path('logo', logo_view, name='logo'),
    path('favicon.ico', empty_view, name='favicon'),
    path('<slug:section_slug>', section_view, name='section'),
    path('<slug:section_slug>/<path:rest>', section_view, name='section-path'),
]

# ################################################################################################################################
# ################################################################################################################################
