# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path
from django.views.generic.base import RedirectView

# Zato
from zato.common.b2b.console.views import console_view
from zato.common.webapp.static import Favicon_Path, static_file

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', RedirectView.as_view(url='/b2b/console/agreements', permanent=False)),
    path('b2b/console/<str:section_slug>', console_view, name='console'),
    path('static/<path:path>', static_file, name='static'),
    path('favicon.ico', RedirectView.as_view(url='/static/' + Favicon_Path, permanent=False)),
]

# ################################################################################################################################
# ################################################################################################################################
