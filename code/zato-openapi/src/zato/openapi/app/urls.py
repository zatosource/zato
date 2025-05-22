# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.urls import path

# Zato
from zato.openapi.app.views import swagger_view, serve_openapi

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', swagger_view, name='swagger'),
    path('openapi.yaml', serve_openapi, name='openapi'),
]

# ################################################################################################################################
# ################################################################################################################################
