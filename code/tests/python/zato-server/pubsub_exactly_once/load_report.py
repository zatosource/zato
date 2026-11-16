# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The measurements of the load tests of exactly-once delivery - rates, transactions per second and latency percentiles,
# logged under one logger so that the results of a run can be read from its log.

# stdlib
import logging
from statistics import quantiles

# Zato
from zato.common.test.pubsub_database import get_db_mode

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_exactly_once.load_report')

# ################################################################################################################################
# ################################################################################################################################

# How many cut points the percentiles are read from, and the cut point of each percentile
_quantile_count = 100
_p50_index = 49
_p95_index = 94
_p99_index = 98

Milliseconds_Per_Second = 1000.0

# ################################################################################################################################
# ################################################################################################################################

class Latencies:
    """ The durations of one kind of operation, in seconds.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self.values:'list[float]' = []

# ################################################################################################################################

    def add(self, value:'float') -> 'None':
        self.values.append(value)

# ################################################################################################################################

    def describe(self) -> 'str':
        """ Returns the count and the percentiles of the durations, in milliseconds.
        """
        cut_points = quantiles(self.values, n=_quantile_count, method='inclusive')

        p50 = cut_points[_p50_index] * Milliseconds_Per_Second
        p95 = cut_points[_p95_index] * Milliseconds_Per_Second
        p99 = cut_points[_p99_index] * Milliseconds_Per_Second
        max_ms = max(self.values) * Milliseconds_Per_Second

        out = f'{self.name} ms - p50 {p50:.1f}, p95 {p95:.1f}, p99 {p99:.1f}, max {max_ms:.1f} (n={len(self.values)})'
        return out

# ################################################################################################################################
# ################################################################################################################################

class LoadReport:
    """ The results of one load test on the pub/sub database of the run.
    """

    def __init__(self, test_name:'str') -> 'None':
        self.test_name = test_name
        self.lines:'list[str]' = []

# ################################################################################################################################

    def add_rate(self, name:'str', count:'int', seconds:'float', unit:'str') -> 'None':
        """ Adds the number of operations of one kind per second.
        """
        rate = count / seconds
        self.lines.append(f'{name} - {rate:.1f} {unit}/s ({count} in {seconds:.1f}s)')

# ################################################################################################################################

    def add_latencies(self, latencies:'Latencies') -> 'None':
        self.lines.append(latencies.describe())

# ################################################################################################################################

    def add_value(self, name:'str', value:'str') -> 'None':
        self.lines.append(f'{name} - {value}')

# ################################################################################################################################

    def log(self) -> 'None':
        """ Logs every result under the name of the test and the database mode.
        """
        db_mode = get_db_mode()

        for line in self.lines:
            logger.info('Load result %s on %s: %s', self.test_name, db_mode, line)

# ################################################################################################################################
# ################################################################################################################################
