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
    """ The shared webapp UI kit - any dashboard that lists this application in INSTALLED_APPS
    gets its templates and static files through the standard Django loaders.
    """
    name = 'zato.common.webapp.ui'
    label = 'zato_common_webapp_ui'

# ################################################################################################################################
# ################################################################################################################################
