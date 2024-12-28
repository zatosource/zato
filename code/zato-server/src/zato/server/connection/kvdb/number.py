# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from datetime import datetime
from logging import getLogger
from operator import add as op_add, gt as op_gt, lt as op_lt, sub as op_sub

# Zato
from zato.common.api import StatsKey
from zato.common.typing_ import dataclass
from zato.server.connection.kvdb.core import BaseRepo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, callnone

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

max_value = sys.maxsize

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
    def __init__(
        self,
        name,      # type: str
        data_path, # type: str
        sync_threshold=120_000, # type: int
        sync_interval=120_000,  # type: int
        max_value=max_value,    # type: int
        allow_negative=True     # type: bool
    ) -> 'None':

        super().__init__(name, data_path, sync_threshold, sync_interval)

        # We will never allow for a value to be greater than that
        self.max_value = max_value

        # If False, value will never be less than zero
        self.allow_negative = allow_negative

        # Main in-RAM database of objects
        self.in_ram_store = {
            _stats_key_current_value: {},
        } # type: anydict

        self.current_value = self.in_ram_store[_stats_key_current_value] # type: anydict

# ################################################################################################################################

    def _change_value(
        self,
        value_op,    # type: callable_
        cmp_op,      # type: callable_
        value_limit, # type: int
        key,         # type: any_
        change_by,   # type: int
        value_limit_condition=None, # type: callnone
        default_value=0 # type: int
    ) -> 'int':

        # Get current value ..
        current_data = self.current_value.get(key) # type: any_

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

        # .. update the last used time as well ..
        current_data[_stats_key_per_key_last_timestamp] = utcnow().isoformat()

        # .. store the new value in RAM ..
        self.current_value[key] = current_data

        # .. update metadata  ..
        self.post_modify_state()

        # .. finally, return the value set.
        return current_data[_stats_key_per_key_value]

# ################################################################################################################################

    def _is_negative_allowed(self) -> 'bool':
        return self.allow_negative

# ################################################################################################################################

    def _incr(self, key:'str', change_by:'int'=1) -> 'int':

        value_op = op_add
        cmp_op   = op_gt
        value_limit = self.max_value

        return self._change_value(value_op, cmp_op, value_limit, key, change_by)

# ################################################################################################################################

    def _decr(self, key:'str', change_by:'int'=1) -> 'int':

        value_op = op_sub
        cmp_op   = op_lt
        value_limit = 0

        return self._change_value(value_op, cmp_op, value_limit, key, change_by, self._is_negative_allowed)

# ################################################################################################################################

    def _get(self, key:'str') -> 'anydict':
        return self.current_value.get(key) # type: ignore

# ################################################################################################################################

    def _remove_all(self) -> 'None':
        self.current_value.clear()

# ################################################################################################################################

    def _clear(self):
        # type: () -> None
        for key in self.in_ram_store: # type: str
            self.in_ram_store[key] = 0

# ################################################################################################################################
# ################################################################################################################################
