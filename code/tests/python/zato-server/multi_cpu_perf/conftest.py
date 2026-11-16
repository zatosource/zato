# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The helpers of the suite, which the tests import as modules of their own
sys.path.insert(0, os.path.dirname(__file__))

# Zato
from zato.common.test.conftest_base_multi_cpu import remove_interrupted_run_state
from zato.common.test.resume import pytest_runtest_protocol as pytest_runtest_protocol
from zato.common.test.resume import pytest_runtest_teardown as pytest_runtest_teardown

# ################################################################################################################################
# ################################################################################################################################

remove_interrupted_run_state()

# ################################################################################################################################
# ################################################################################################################################
