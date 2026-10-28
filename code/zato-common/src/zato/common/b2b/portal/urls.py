# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path

# Zato
from zato.common.b2b.portal.views import asset_view, empty_view, section_view

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', section_view, {'section_slug': 'messages'}, name='messages'),
    path('alerts', section_view, {'section_slug': 'alerts'}, name='alerts'),
    path('partners', section_view, {'section_slug': 'partners'}, name='partners'),
    path('agreements', section_view, {'section_slug': 'agreements'}, name='agreements'),
    path('registrations', section_view, {'section_slug': 'registrations'}, name='registrations'),
    path('alert-rules', section_view, {'section_slug': 'alert-rules'}, name='alert-rules'),
    path('assets/<path:path>', asset_view, name='asset'),
    path('favicon.ico', empty_view, name='favicon'),
]

# ################################################################################################################################
# ################################################################################################################################
