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

# Zato
from zato.common.typing_ import dataclass
from zato.server.connection.kvdb.core import BaseRepo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

current_value_key = 'current_value'
current_usage_key = 'current_usage'

usage_time_format = '%Y-%m-%d %H:%M'

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
            current_value_key: {},
            current_usage_key: {},
        }

        self.current_value = self.in_ram_store[current_value_key] # type: dict
        self.current_usage = self.in_ram_store[current_usage_key] # type: dict

# ################################################################################################################################

    def sync_state(self):
        # type: () -> None
        with self.update_lock:
            print()
            print(222, self.current_usage)
            print()
            pass

# ################################################################################################################################

    def _update_key_usage(self, key):
        # type: (str) -> None

        now = utcnow()
        now = now.strftime(usage_time_format)

        by_minute = self.current_usage.setdefault(now, {}) # type: dict
        current_key_usage = by_minute.setdefault(key, 0)
        by_minute[key] = current_key_usage + 1

# ################################################################################################################################

    def _change_value(self, value_op, cmp_op, value_limit, key, change_by, value_limit_condition=None, default_value=0):
        # type: (object, object, int, str, int, object) -> int

        # Get current value or default to 0, if nothing is found ..
        default = {
            'value':default_value,
            'last_timestamp':utcnow().isoformat(),
            'last_duration':-1
        }
        current_data = self.current_value.get(key, default)

        # .. get the new value ..
        current_data['value'] = value_op(current_data['value'], change_by)

        # .. does the new value exceed the limit? ..
        is_limit_exceeded = cmp_op(current_data['value'], value_limit)

        # .. we may have a condition function that tells us whether to allow the new value beyond the limit ..
        if value_limit_condition and value_limit_condition():

            # Do nothing because we already have the new value
            # and we merely confirmed that it should not be changed
            # due to its reaching a limit.
            pass

        # .. otherwise, without such a function, we do not allow it ..
        else:
            if is_limit_exceeded:
                current_data['value'] = value_limit

        # .. store the new value in RAM ..
        self.current_value[key] = current_data

        # .. update usage statistics ..
        self._update_key_usage(key)

        # .. update metadata and possibly trim statistics ..
        self.post_modify_state()

        # .. finally, return the value set.
        return current_data['value']

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

    def _get(self, key, default=0):
        # type: (str, int) -> int
        return self.current_value.get(key, default)

# ################################################################################################################################

    def _remove_all(self):
        # type: () -> None
        self.current_value.clear()
        self.current_usage.clear()

# ################################################################################################################################

    def _clear(self):
        # type: () -> None
        for key in self.in_ram_store: # type: str
            self.in_ram_store[key] = 0

# ################################################################################################################################

    def set_last_duration(self, key, value):
        # type: (str, int) -> None
        with self.update_lock:
            self.current_value[key]['last_duration'] = value

# ################################################################################################################################
# ################################################################################################################################
