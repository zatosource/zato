# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _live_tests import live_test

# ################################################################################################################################
# ################################################################################################################################

test_claim_contention = live_test('test_reliability', 'test_claim_contention')
test_smb_service_restart = live_test('test_reliability', 'test_smb_service_restart')
test_port_blocked = live_test('test_reliability', 'test_port_blocked')
test_guest_paused = live_test('test_reliability', 'test_guest_paused')
test_credential_rotation = live_test('test_reliability', 'test_credential_rotation')
test_share_removed = live_test('test_reliability', 'test_share_removed')

# ################################################################################################################################
# ################################################################################################################################
