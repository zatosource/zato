# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

try:
    # Try to use the stdlib first ..
    from dataclasses import *

except ImportError:
    # .. fall back to our own vendor copy on Python < 3.7
    from zato.common.ext.dataclasses import *
