# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

""" The tests of the live suite in test_write_modes.py, run against the peer in place of a Zato server.
"""

# Local
from test_write_modes import test_temp_then_rename, test_slow_writer, test_locked_file

# ##############################################################################################################################
# ##############################################################################################################################

__all__ = [
    'test_temp_then_rename',
    'test_slow_writer',
    'test_locked_file',
]

# ##############################################################################################################################
# ##############################################################################################################################
