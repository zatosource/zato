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

if 0:
    from zato.common.typing_ import strtuple

# ################################################################################################################################
# ################################################################################################################################

nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class _ExpectedRecordFilter(logging.Filter):
    """ Puts the marker of expected records in front of the message of each record of a logger, or of each record
    whose message contains one of the given fragments, so that the log counter of the tests does not count
    the warnings and errors that a test causes on purpose.
    """
    def __init__(self, fragments:'strtuple') -> 'None':
        super().__init__()
        self.fragments = fragments

    def filter(self, record:'logging.LogRecord') -> 'bool':

        # A record that contains none of the fragments, if there are any, passes on unmarked ..
        if self.fragments:
            message = record.getMessage()

            for fragment in self.fragments:
                if fragment in message:
                    break
            else:
                return True

        # .. and every other record passes on with the marker.
        record.msg = f'{Expected_Record_Marker} {record.msg}'
        return True

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def expected_records(logger_name:'str', fragments:'strtuple'=()) -> 'nonegen':
    """ Marks each record of the named logger as expected while the block runs, or, if fragments are given,
    each record whose message contains one of them.
    """
    logger = logging.getLogger(logger_name)
    record_filter = _ExpectedRecordFilter(fragments)

    logger.addFilter(record_filter)

    try:
        yield
    finally:
        logger.removeFilter(record_filter)

# ################################################################################################################################
# ################################################################################################################################
