# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.apps import AppConfig

# ################################################################################################################################
# ################################################################################################################################

class WebappUIConfig(AppConfig):
    """ The shared webapp UI kit - registering this app gives a dashboard the UI kernel scripts,
    the token-based css, the generated themes and the base template through the standard Django loaders.
    """
    name = 'zato.common.webapp.ui'
    label = 'zato_common_webapp_ui'

# ################################################################################################################################
# ################################################################################################################################
