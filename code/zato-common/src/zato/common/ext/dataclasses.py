# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Be explicit about which import error we want to catch
try:
    import dataclasses

# Python 3.6
except ImportError:
    from zato.common.ext.dataclasses import *

# Python 3.6+
else:
    from dataclasses import *
