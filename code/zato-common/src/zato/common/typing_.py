# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

#
# Dataclasses
#

# This will always succeed
from dacite import from_dict

try:
    # Try to use the stdlib first ..
    from dataclasses import * # noqa: F401

except ImportError:
    # .. fall back to our own vendor copy on Python < 3.7
    from zato.common.ext.dataclasses import * # noqa: F401

# For flake8
from_dict = from_dict

# ################################################################################################################################
# ################################################################################################################################

#
# TypedDict
#
try:
    from typing import TypedDict
except ImportError:
    from zato.common.ext.typing_extensions import TypedDict

# For flake8
TypedDict = TypedDict

# ################################################################################################################################
# ################################################################################################################################
