# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import contextmanager
from typing import Generator

# Zato
from zato.common.test.conftest_base_pubsub import Expected_Record_Marker

# ################################################################################################################################
# ################################################################################################################################

nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class _ExpectedRecordFilter(logging.Filter):
    """ Puts the marker of expected records in front of the message of each record of a logger,
    so that the log counter of the tests does not count the warnings and errors that a test causes on purpose.
    """
    def filter(self, record:'logging.LogRecord') -> 'bool':
        record.msg = f'{Expected_Record_Marker} {record.msg}'
        return True

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def expected_records(logger_name:'str') -> 'nonegen':
    """ Marks each record of the named logger as expected while the block runs.
    """
    logger = logging.getLogger(logger_name)
    record_filter = _ExpectedRecordFilter()

    logger.addFilter(record_filter)

    try:
        yield
    finally:
        logger.removeFilter(record_filter)

# ################################################################################################################################
# ################################################################################################################################
