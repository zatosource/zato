# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import warnings

# These fire at import time from third-party code outside our control.
# The filters must be installed before any test module is collected.
warnings.filterwarnings('ignore', message='.*urllib3.contrib.pyopenssl.*')
warnings.filterwarnings('ignore', message='.*datetime.datetime.utcnow.*')
