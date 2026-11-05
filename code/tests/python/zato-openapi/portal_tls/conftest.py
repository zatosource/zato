# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# ################################################################################################################################
# ################################################################################################################################

# Pytest imports test modules with importlib, which does not make this directory importable on its own
_conftest_dir = os.path.dirname(__file__)
sys.path.insert(0, _conftest_dir)

# Zato
from portal_tls_origins import Trusted_Origin_First, Trusted_Origin_Second, Trusted_Origins_Env_Key # noqa: E402

# ################################################################################################################################

# The portal reads its trusted origins when its settings are imported, so they are in the environment before Django starts
os.environ[Trusted_Origins_Env_Key] = f' {Trusted_Origin_First} , {Trusted_Origin_Second} '
os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.openapi.app.settings'

# ################################################################################################################################

# Django
import django # noqa: E402

django.setup()

# ################################################################################################################################
# ################################################################################################################################
