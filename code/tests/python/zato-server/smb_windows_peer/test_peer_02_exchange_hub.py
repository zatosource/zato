# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.live_tests import live_test

# ################################################################################################################################
# ################################################################################################################################

test_single_file = live_test('test_exchange_hub', 'test_single_file')
test_burst = live_test('test_exchange_hub', 'test_burst')
test_fan_out = live_test('test_exchange_hub', 'test_fan_out')
test_empty_file_rejected = live_test('test_exchange_hub', 'test_empty_file_rejected')

# ################################################################################################################################
# ################################################################################################################################
