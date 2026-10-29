# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import gc
import os
import sys
from collections import Counter, deque
from json import dumps
from threading import Lock
from time import time

# gevent
from gevent import sleep, spawn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from io import TextIOWrapper
    from zato.common.typing_ import stranydict
    stranydict = stranydict
    TextIOWrapper = TextIOWrapper

# ################################################################################################################################
# ################################################################################################################################

floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

# Prototype - the path prefix of the timing log of each process, which is disabled when the variable is not set.
Env_Commit_Timing_Path = 'Zato_B2B_Commit_Timing_Path'

# How often the event loop probe wakes up, and how often it writes what it measured.
_loop_probe_interval_seconds = 0.05
_loop_report_interval_seconds = 10.0

# Garbage collections shorter than this are not written.
_gc_report_threshold_ms = 5.0

_page_size = os.sysconf('SC_PAGE_SIZE')

# How often the live objects are counted by type, and how many of the most numerous types are written.
_census_interval_seconds = 300.0
_census_top_count = 30

# How many of the largest containers the census writes.
_census_container_count = 15

_container_types = (list, dict, set, frozenset, deque, tuple)

# ################################################################################################################################
# ################################################################################################################################

class TimingLog:
    """ Appends one JSON line per timing record to a file of this process.
    """

    def __init__(self, path:'str') -> 'None':
        self._file:'TextIOWrapper' = open(path, 'a', buffering=1, encoding='utf8')
        self._lock = Lock()
        self._gc_started_at = 0.0

# ################################################################################################################################

    def write(self, record:'stranydict') -> 'None':
        record['at'] = time()
        line = dumps(record)

        with self._lock:
            _ = self._file.write(line + '\n')

# ################################################################################################################################

    def _run_loop_probe(self) -> 'None':
        """ Measures by how much each sleep of the event loop overruns its interval, and writes the average,
        the maximum and the number of samples of each reporting interval.
        """
        lags:'floatlist' = []
        reported_at = time()

        while True:
            started_at = time()
            sleep(_loop_probe_interval_seconds)
            now = time()

            lag = now - started_at - _loop_probe_interval_seconds
            lags.append(lag * 1000)

            if now - reported_at >= _loop_report_interval_seconds:
                with open('/proc/self/statm') as statm:
                    resident_pages = int(statm.read().split()[1])

                self.write({
                    'type': 'loop',
                    'avg_ms': round(sum(lags) / len(lags), 2),
                    'max_ms': round(max(lags), 2),
                    'samples': len(lags),
                    'rss_mb': round(resident_pages * _page_size / 1048576, 1),
                    'allocated_blocks': sys.getallocatedblocks(),
                    'gc_collections': [item['collections'] for item in gc.get_stats()],
                })
                lags = []
                reported_at = now

# ################################################################################################################################

    def _on_gc(self, phase:'str', info:'stranydict') -> 'None':
        """ Writes the duration of each garbage collection that exceeds the threshold.
        """
        if phase == 'start':
            self._gc_started_at = time()
            return

        duration_ms = (time() - self._gc_started_at) * 1000

        if duration_ms >= _gc_report_threshold_ms:
            self.write({
                'type': 'gc',
                'generation': info['generation'],
                'ms': round(duration_ms, 2),
                'collected': info['collected'],
                'tracked': len(gc.get_objects(info['generation'])),
            })

# ################################################################################################################################

    def _run_census(self) -> 'None':
        """ Writes the number of live objects of each of the most numerous types, and how long counting them took.
        """
        while True:
            sleep(_census_interval_seconds)

            started_at = time()
            objects = gc.get_objects()
            counts = Counter(type(item).__name__ for item in objects)
            duration_ms = (time() - started_at) * 1000

            containers = [item for item in objects if isinstance(item, _container_types)]
            container_items = sum(len(item) for item in containers)
            largest = sorted(containers, key=len, reverse=True)[:_census_container_count]

            largest_out = [{'type': type(item).__name__, 'len': len(item)} for item in largest]

            del objects, containers, largest

            self.write({
                'type': 'census',
                'ms': round(duration_ms, 2),
                'total': sum(counts.values()),
                'allocated_blocks': sys.getallocatedblocks(),
                'container_items': container_items,
                'largest': largest_out,
                'top': counts.most_common(_census_top_count),
            })

# ################################################################################################################################

    def start_loop_probe(self) -> 'None':
        gc.callbacks.append(self._on_gc)
        _ = spawn(self._run_loop_probe)
        _ = spawn(self._run_census)

# ################################################################################################################################
# ################################################################################################################################

def _new_timing_log() -> 'TimingLog | None':
    if path := os.environ.get(Env_Commit_Timing_Path, ''):
        out = TimingLog(f'{path}.{os.getpid()}.jsonl')
    else:
        out = None

    return out

# The timing log of this process, if the environment enables it.
timing_log = _new_timing_log()

# ################################################################################################################################
# ################################################################################################################################
