# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.urls import path

# Zato
from zato.openapi.app.views import openapi_spec, swagger_ui

urlpatterns = [
    path('', swagger_ui, name='swagger_ui'),
    path('spec/', openapi_spec, name='openapi_spec'),
]
