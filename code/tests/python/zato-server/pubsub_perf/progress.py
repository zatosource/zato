# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from threading import Event
    from zato.common.typing_ import callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_perf.progress')

sourcelist = list['_Source']

# ################################################################################################################################
# ################################################################################################################################

# How often the progress of a test is logged, in seconds
_interval_seconds = 10.0

# ################################################################################################################################
# ################################################################################################################################

class _Source(NamedTuple):
    """ One count that the progress of a test reports.
    """
    name: 'str'
    read: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

class Progress:
    """ Logs the counts of a running test at regular intervals, so that a run that stalls can be told from one
    that is still working. The figures of the run are recorded only once it completes.
    """

    def __init__(self, test_name:'str') -> 'None':
        self.test_name = test_name
        self.sources:'sourcelist' = []

# ################################################################################################################################

    def add_count(self, name:'str', read:'callable_') -> 'None':
        source = _Source(name, read)
        self.sources.append(source)

# ################################################################################################################################

    def run(self, stop:'Event') -> 'None':
        """ Logs the counts at each interval until the test stops it.
        """
        start = time.monotonic()

        while not stop.wait(_interval_seconds):

            parts:'strlist' = []

            for source in self.sources:
                value = source.read()
                parts.append(f'{source.name}={value}')

            elapsed = time.monotonic() - start
            description = ', '.join(parts)

            logger.info('Progress of %s at %.0fs: %s', self.test_name, elapsed, description)

# ################################################################################################################################
# ################################################################################################################################
