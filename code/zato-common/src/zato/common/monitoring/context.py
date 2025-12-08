# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.typing_ import strdict
from zato.common.monitoring.metrics import get_global_metrics_store

# ################################################################################################################################
# ################################################################################################################################

class ProcessContext:
    """ Context object for process instance metrics operations.
    """

    def __init__(self, process_name:'str', ctx_id:'str') -> 'None':
        self.process_name = process_name
        self.ctx_id = ctx_id
        self._metrics_store = get_global_metrics_store()

    def push(self, key:'str', value:'float') -> 'None':
        """ Set metric value.
        """
        self._metrics_store.set_value(self.process_name, self.ctx_id, key, value)

    def push_dict(self, metrics:'strdict') -> 'None':
        """ Set multiple metric values from dictionary.
        """
        for key, value in metrics.items():
            self.push(key, value)

    def incr(self, key:'str') -> 'None':
        """ Increment metric by 1.
        """
        self._metrics_store.increment_value(self.process_name, self.ctx_id, key, 1.0)

    def incr_by(self, key:'str', amount:'float') -> 'None':
        """ Increment metric by specified amount.
        """
        self._metrics_store.increment_value(self.process_name, self.ctx_id, key, amount)

    def decr(self, key:'str') -> 'None':
        """ Decrement metric by 1.
        """
        self._metrics_store.decrement_value(self.process_name, self.ctx_id, key, 1.0)

    def decr_by(self, key:'str', amount:'float') -> 'None':
        """ Decrement metric by specified amount.
        """
        self._metrics_store.decrement_value(self.process_name, self.ctx_id, key, amount)

    def set_max(self, key:'str', value:'float') -> 'None':
        """ Update metric only if new value exceeds current.
        """
        self._metrics_store.set_max_value(self.process_name, self.ctx_id, key, value)

    def set_min(self, key:'str', value:'float') -> 'None':
        """ Update metric only if new value is below current.
        """
        self._metrics_store.set_min_value(self.process_name, self.ctx_id, key, value)

    def push_duration(self, key:'str', milliseconds:'float') -> 'None':
        """ Record duration in milliseconds.
        """
        self.push(key, milliseconds)

    def push_timestamp(self, key:'str') -> 'None':
        """ Record current unix timestamp.
        """
        self.push(key, time.time())

    def timer_start(self, key:'str') -> 'None':
        """ Start internal timer for key.
        """
        self._metrics_store.timer_start(self.process_name, self.ctx_id, key)

    def timer_stop(self, key:'str') -> 'None':
        """ Stop timer and record elapsed milliseconds.
        """
        self._metrics_store.timer_stop(self.process_name, self.ctx_id, key)

# ################################################################################################################################
# ################################################################################################################################

class GlobalMetrics:
    """ Global metrics not tied to specific process instance.
    """

    def __init__(self) -> 'None':
        self._metrics_store = get_global_metrics_store()

    def incr_global(self, key:'str') -> 'None':
        """ Increment global metric by 1.
        """
        self._metrics_store.increment_value('global', '', key, 1.0)

    def decr_global(self, key:'str') -> 'None':
        """ Decrement global metric by 1.
        """
        self._metrics_store.decrement_value('global', '', key, 1.0)

    def push_global(self, key:'str', value:'float') -> 'None':
        """ Set global metric value.
        """
        self._metrics_store.set_value('global', '', key, value)

# ################################################################################################################################
# ################################################################################################################################

# Global metrics instance
_global_metrics = GlobalMetrics()

# ################################################################################################################################
# ################################################################################################################################

def get_global_metrics() -> 'GlobalMetrics':
    """ Get global metrics instance.
    """
    return _global_metrics

# ################################################################################################################################
# ################################################################################################################################
