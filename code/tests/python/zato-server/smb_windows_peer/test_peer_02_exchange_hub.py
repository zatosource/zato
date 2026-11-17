# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

""" The tests of the live suite in test_exchange_hub.py, run against the peer in place of a Zato server.
"""

# Local
from test_exchange_hub import test_single_file, test_burst, test_fan_out, test_empty_file_rejected

# ##############################################################################################################################
# ##############################################################################################################################

__all__ = [
    'test_single_file',
    'test_burst',
    'test_fan_out',
    'test_empty_file_rejected',
]

# ##############################################################################################################################
# ##############################################################################################################################
