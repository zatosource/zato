# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The suite's own helpers, e.g. audit_env, must be importable no matter where pytest runs from.
suite_dir = os.path.dirname(__file__)
sys.path.insert(0, suite_dir)

# The environment helpers are shared with the zato-common suites.
common_lib_dir = os.path.join(suite_dir, '..', '..', 'zato-common', 'lib')
common_lib_dir = os.path.abspath(common_lib_dir)
sys.path.insert(0, common_lib_dir)

# ################################################################################################################################
# ################################################################################################################################
