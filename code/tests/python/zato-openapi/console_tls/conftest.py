# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

# The console reads its trusted origins when its settings are imported, so they are in the environment before Django starts
Trusted_Origins_Env_Key = 'Zato_OpenAPI_Console_CSRF_Trusted_Origins'
Trusted_Origin_First    = 'https://api-docs.example.com'
Trusted_Origin_Second   = 'https://portal.example.com:9443'

os.environ[Trusted_Origins_Env_Key] = f' {Trusted_Origin_First} , {Trusted_Origin_Second} '
os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.openapi.app.settings'

# ################################################################################################################################

# Django
import django

django.setup()

# ################################################################################################################################
# ################################################################################################################################
