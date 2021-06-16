# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from datetime import datetime
from logging import getLogger
from operator import add as op_add, gt as op_gt, lt as op_lt, sub as op_sub

# numpy
import numpy as np

# Zato
from zato.common.api import StatsKey
from zato.common.typing_ import dataclass
from zato.server.connection.kvdb.core import BaseRepo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

_stats_key_current_value = StatsKey.CurrentValue

_stats_key_per_key_min   = StatsKey.PerKeyMin
_stats_key_per_key_max   = StatsKey.PerKeyMax
_stats_key_per_key_mean  = StatsKey.PerKeyMean

_stats_key_per_key_value          = StatsKey.PerKeyValue
_stats_key_per_key_last_timestamp = StatsKey.PerKeyLastTimestamp
_stats_key_per_key_last_duration  = StatsKey.PerKeyLastDuration

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class IntData:
    value: int
    timestamp: str
    last_duration: int

# ################################################################################################################################
# ################################################################################################################################

class NumberRepo(BaseRepo):
    """ Stores integer counters for string labels.
    """
    def __init__(self, name, sync_threshold=120_000, sync_interval=120_000, max_value=sys.maxsize, allow_negative=True):
        # type: (str, int, int, int, int) -> None
        super().__init__(name, sync_threshold, sync_interval)

        # We will never allow for a value to be greater than that
        self.max_value = max_value

        # If False, value will never be less than zero
        self.allow_negative = allow_negative

        # Main in-RAM database of objects
        self.in_ram_store = {
            _stats_key_current_value: {},
        }
        self.current_value = self.in_ram_store[_stats_key_current_value] # type: dict

# ################################################################################################################################

    def _change_value(self, value_op, cmp_op, value_limit, key, change_by, value_limit_condition=None, default_value=0):
        # type: (object, object, int, str, int, object) -> int

        # Get current value ..
        current_data = self.current_value.get(key)

        # .. or set a default to 0, if nothing is found ..
        if not current_data:

            # .. zero out all the counters ..
            current_data = {

                _stats_key_per_key_value: default_value,
                _stats_key_per_key_last_timestamp: utcnow().isoformat(),
                _stats_key_per_key_last_duration: None,

                _stats_key_per_key_min:  None,
                _stats_key_per_key_max:  None,
                _stats_key_per_key_mean: None,
            }

            # .. and assign them to our key ..
            self.current_value[key] = current_data

        # .. get the new value ..
        current_data[_stats_key_per_key_value] = value_op(current_data[_stats_key_per_key_value], change_by)

        # .. does the new value exceed the limit? ..
        is_limit_exceeded = cmp_op(current_data[_stats_key_per_key_value], value_limit)

        # .. we may have a condition function that tells us whether to allow the new value beyond the limit ..
        if value_limit_condition and value_limit_condition():

            # Do nothing because we already have the new value
            # and we merely confirmed that it should not be changed
            # due to its reaching a limit.
            pass

        # .. otherwise, without such a function, we do not allow it ..
        else:
            if is_limit_exceeded:
                current_data[_stats_key_per_key_value] = value_limit

        # .. store the new value in RAM ..
        self.current_value[key] = current_data

        # .. update metadata and possibly trim statistics ..
        self.post_modify_state()

        # .. finally, return the value set.
        return current_data[_stats_key_per_key_value]

# ################################################################################################################################

    def _is_negative_allowed(self):
        # type: (int) -> bool
        return self.allow_negative

# ################################################################################################################################

    def _incr(self, key, change_by=1):
        # type: (str, int) -> int

        value_op = op_add
        cmp_op   = op_gt
        value_limit = self.max_value

        return self._change_value(value_op, cmp_op, value_limit, key, change_by)

# ################################################################################################################################

    def _decr(self, key, change_by=1):
        # type: (str, int) -> int

        value_op = op_sub
        cmp_op   = op_lt
        value_limit = 0

        return self._change_value(value_op, cmp_op, value_limit, key, change_by, self._is_negative_allowed)

# ################################################################################################################################

    def _get(self, key):
        # type: (str) -> dict
        return self.current_value.get(key)

# ################################################################################################################################

    def _remove_all(self):
        # type: () -> None
        self.current_value.clear()

# ################################################################################################################################

    def _clear(self):
        # type: () -> None
        for key in self.in_ram_store: # type: str
            self.in_ram_store[key] = 0

# ################################################################################################################################

    def set_last_duration(self, key, current_duration):
        # type: (str, int) -> None
        with self.update_lock:

            per_key_dict = self.current_value[key]
            previous_duration = per_key_dict[_stats_key_per_key_last_duration]

            if previous_duration:
                to_compare = [previous_duration, current_duration]
                new_min  = min(to_compare)
                new_max  = max(to_compare)
                new_mean = np.mean(to_compare)
            else:
                new_min  = current_duration
                new_max  = current_duration
                new_mean = current_duration

            # We need to check the exact class here instead of using isinstance(new_mean, float)
            # because numpy.float64 is a subclass of float. It is good when the mean
            # is used in computations but when it comes to JSON serialisation it really
            # needs to be a float rather than np.float64. That is why here we turn float64 into a real float.
            new_mean = new_mean if new_mean.__class__ is float else new_mean.item()

            per_key_dict[_stats_key_per_key_last_duration] = current_duration
            per_key_dict[_stats_key_per_key_min]  = new_min
            per_key_dict[_stats_key_per_key_max]  = new_max
            per_key_dict[_stats_key_per_key_mean] = new_mean

# ################################################################################################################################
# ################################################################################################################################
