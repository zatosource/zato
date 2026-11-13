# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fixtures of the suite comparing the REST channel router with the request dispatcher.

# stdlib
import logging
import os
import sys

# pytest
import pytest

_suite_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _suite_directory)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_logger_names = ['', 'zato_rest']

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True, scope='session')
def info_logging() -> 'any_':
    """ Makes the loggers of the dispatcher emit their INFO records, and restores their levels at the end.
    """
    levels = {}

    for name in _logger_names:
        logger = logging.getLogger(name)
        levels[name] = logger.level
        logger.setLevel(logging.INFO)

    yield

    for name, level in levels.items():
        logger = logging.getLogger(name)
        logger.setLevel(level)

# ################################################################################################################################
# ################################################################################################################################
