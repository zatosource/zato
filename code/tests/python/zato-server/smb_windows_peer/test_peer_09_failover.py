# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

""" The tests of the live suite in test_failover.py, run against the peer in place of a Zato server.
"""

# Local
from test_failover import test_server_restart, test_switchover

# ##############################################################################################################################
# ##############################################################################################################################

__all__ = [
    'test_server_restart',
    'test_switchover',
]

# ##############################################################################################################################
# ##############################################################################################################################
