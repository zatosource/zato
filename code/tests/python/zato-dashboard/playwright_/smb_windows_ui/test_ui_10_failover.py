# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyTest
import pytest

# Zato
from live_windows.live_tests import live_test

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Dashboard retries each call to the server while the server restarts
    Restart_Retry = "after connection broken by 'NewConnectionError"

# ################################################################################################################################
# ################################################################################################################################

_expect_restart_retries = pytest.mark.expect_log_errors(ModuleCtx.Restart_Retry)

test_server_restart = _expect_restart_retries(live_test('test_failover', 'test_server_restart'))
test_switchover = live_test('test_failover', 'test_switchover')

# ################################################################################################################################
# ################################################################################################################################
