# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# flake8: noqa

# Be explicit about which import error we want to catch
try:
    import dataclasses

# Python 3.6
except ImportError:
    from zato.common.ext._dataclasses import _FIELDS, _PARAMS
    from zato.common.ext._dataclasses import * # noqa

# Python 3.6+
else:
    from dataclasses import _FIELDS, _PARAMS
    from dataclasses import *
