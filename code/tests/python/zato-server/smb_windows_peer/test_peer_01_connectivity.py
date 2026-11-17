# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

""" The tests of the live suite in test_connectivity.py, run against the peer in place of a Zato server.
"""

# Local
from test_connectivity import test_agent_responds, test_exchange_account_reaches_every_share, test_round_trip, \
    test_control_share_refused

# ##############################################################################################################################
# ##############################################################################################################################

__all__ = [
    'test_agent_responds',
    'test_exchange_account_reaches_every_share',
    'test_round_trip',
    'test_control_share_refused',
]

# ##############################################################################################################################
# ##############################################################################################################################
