# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The environment helpers are shared with the zato-common audit log suite
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# Django
from django.conf import settings

# The views build responses and read the request the way Django hands it over, so Django is
# configured before anything imports them - with nothing behind it, no database and no
# templates, because a view is called here directly rather than through a URL.
if not settings.configured:
    settings.configure(
        DEBUG=False,
        DATABASES={},
        INSTALLED_APPS=[],
        USE_TZ=True,
        DEFAULT_CHARSET='utf-8',
    )

# ################################################################################################################################
# ################################################################################################################################
