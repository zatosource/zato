# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from statistics import quantiles

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many cut points the percentiles are read from, and the cut point of each percentile
_quantile_count = 100
_p50_index = 49
_p95_index = 94
_p99_index = 98

# How many milliseconds a second has
_milliseconds_per_second = 1000.0

# ################################################################################################################################
# ################################################################################################################################

class Latencies:
    """ The durations of one kind of operation, in seconds.
    """

    def __init__(self) -> 'None':
        self.values:'list[float]' = []

# ################################################################################################################################

    def add(self, value:'float') -> 'None':
        self.values.append(value)

# ################################################################################################################################

    def get_figures(self) -> 'stranydict':
        """ Returns the count and the percentiles of the durations, in milliseconds.
        """
        cut_points = quantiles(self.values, n=_quantile_count, method='inclusive')

        out:'stranydict' = {
            'count': len(self.values),
            'p50_ms': cut_points[_p50_index] * _milliseconds_per_second,
            'p95_ms': cut_points[_p95_index] * _milliseconds_per_second,
            'p99_ms': cut_points[_p99_index] * _milliseconds_per_second,
            'max_ms': max(self.values) * _milliseconds_per_second,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

def get_rate_figures(count:'int', seconds:'float') -> 'stranydict':
    """ Returns how many operations of one kind took place, in how many seconds, and how many per second.
    """
    out:'stranydict' = {
        'count': count,
        'seconds': seconds,
        'per_second': count / seconds,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
