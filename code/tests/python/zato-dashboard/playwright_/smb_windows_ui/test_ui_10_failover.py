# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyTest
import pytest

# Zato
from live_windows.live_tests import live_test

# Test support
from _smb_windows_ui_suite import ModuleCtx as SuiteCtx

# ################################################################################################################################
# ################################################################################################################################

_expect_restart_records = pytest.mark.expect_log_errors(*SuiteCtx.Restart_Records)

test_server_restart = _expect_restart_records(live_test('test_failover', 'test_server_restart'))
test_switchover = live_test('test_failover', 'test_switchover')

# ################################################################################################################################
# ################################################################################################################################
