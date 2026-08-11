# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The Graph simulator lives with the rule engine jobs suite and the environment
# helpers are shared with the zato-common audit log suite.
_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

sys.path.insert(0, os.path.join(_tests_dir, 'zato-common', 'rule_engine_jobs', 'lib'))
sys.path.insert(0, os.path.join(_tests_dir, 'zato-common', 'lib'))

# ################################################################################################################################
# ################################################################################################################################
