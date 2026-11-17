# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _live_tests import live_test

# ################################################################################################################################
# ################################################################################################################################

test_agent_responds = live_test('test_connectivity', 'test_agent_responds')
test_exchange_account_reaches_every_share = live_test('test_connectivity', 'test_exchange_account_reaches_every_share')
test_round_trip = live_test('test_connectivity', 'test_round_trip')
test_control_share_refused = live_test('test_connectivity', 'test_control_share_refused')

# ################################################################################################################################
# ################################################################################################################################
