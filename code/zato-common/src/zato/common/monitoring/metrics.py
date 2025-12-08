# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import time
from threading import RLock
from typing import Dict, Tuple, Optional

class MetricsStore:
    """ Thread-safe storage for process metrics with Prometheus text format export.
    """

    def __init__(self) -> 'None':
        self._metrics: 'Dict[Tuple[str, str, str], float]' = {}
        self._timers: 'Dict[Tuple[str, str, str], float]' = {}
        self._lock = RLock()

    def set_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set metric value for given process, context, and key.
        """
        with self._lock:
            self._metrics[(process_name, ctx_id, key)] = value

    def get_value(self, process_name:'str', ctx_id:'str', key:'str') -> 'Optional[float]':
        """ Get current metric value.
        """
        with self._lock:
            return self._metrics.get((process_name, ctx_id, key))

    def increment_value(self, process_name:'str', ctx_id:'str', key:'str', amount:'float' = 1.0) -> 'None':
        """ Increment metric value by amount.
        """
        with self._lock:
            current = self._metrics.get((process_name, ctx_id, key), 0.0)
            self._metrics[(process_name, ctx_id, key)] = current + amount

    def decrement_value(self, process_name:'str', ctx_id:'str', key:'str', amount:'float' = 1.0) -> 'None':
        """ Decrement metric value by amount.
        """
        with self._lock:
            current = self._metrics.get((process_name, ctx_id, key), 0.0)
            self._metrics[(process_name, ctx_id, key)] = current - amount

    def set_max_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set value only if it exceeds current value.
        """
        with self._lock:
            current = self._metrics.get((process_name, ctx_id, key), float('-inf'))
            if value > current:
                self._metrics[(process_name, ctx_id, key)] = value

    def set_min_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set value only if it is below current value.
        """
        with self._lock:
            current = self._metrics.get((process_name, ctx_id, key), float('inf'))
            if value < current:
                self._metrics[(process_name, ctx_id, key)] = value

    def timer_start(self, process_name:'str', ctx_id:'str', key:'str') -> 'None':
        """ Start timer for given key.
        """
        with self._lock:
            self._timers[(process_name, ctx_id, key)] = time.time()

    def timer_stop(self, process_name:'str', ctx_id:'str', key:'str') -> 'Optional[float]':
        """ Stop timer and record elapsed milliseconds as metric.
        """
        with self._lock:
            start_time = self._timers.pop((process_name, ctx_id, key), None)
            if start_time is not None:
                elapsed_ms = (time.time() - start_time) * 1000.0
                self._metrics[(process_name, ctx_id, key)] = elapsed_ms
                return elapsed_ms
            return None

    def get_prometheus_format(self) -> 'str':
        """ Export all metrics in Prometheus text format.
        """
        with self._lock:
            if not self._metrics:
                return '# No metrics available\n'

            lines = ['# HELP process_value Process metric values']
            lines.append('# TYPE process_value gauge')

            for (process_name, ctx_id, key), value in sorted(self._metrics.items()):
                if ctx_id:
                    line = f'process_value{{process_name=\'{process_name}\',ctx_id=\'{ctx_id}\',key=\'{key}\'}} {value}'
                else:
                    line = f'process_value{{process_name=\'{process_name}\',key=\'{key}\'}} {value}'
                lines.append(line)

            return '\n'.join(lines) + '\n'

# Global metrics store instance
_global_metrics_store = MetricsStore()

def get_global_metrics_store() -> 'MetricsStore':
    """ Get the global metrics store instance.
    """
    return _global_metrics_store
