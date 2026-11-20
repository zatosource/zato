# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A publisher that records the time of each acknowledgment and of each error, by which a test establishes
# when a pair acknowledged publications and when it refused them.

# stdlib
import threading
import time

# Zato
from workload import Topic_Name, Unpaced_Interval
from zato.common.test.client import PublishClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the publisher waits after an error before the next publication, in seconds
    Error_Pause = 0.2

# ################################################################################################################################
# ################################################################################################################################

def get_percentile(values:'list[float]', percentile:'float') -> 'float':
    """ Returns the given percentile of sorted values, or 0.0 if there are none.
    """
    if not values:
        return 0.0

    index = int(len(values) * percentile)
    index = min(index, len(values) - 1)

    out = values[index]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TimedPublisher:
    """ Publishes one message after another to one address, with the given pause after each acknowledged one,
    and records when each one succeeded or failed.
    """

    def __init__(self, base_url:'str', username:'str', password:'str', interval:'float'=Unpaced_Interval) -> 'None':
        self.client = PublishClient(base_url, username, password)
        self.interval = interval
        self.lock = threading.Lock()
        self.is_running = threading.Event()

        # The acknowledged publications, with the time each request was sent and the time it returned,
        # and the times at which requests failed.
        self.acknowledged:'list[tuple[float, float, str]]' = []
        self.errors:'list[float]' = []

        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def _run(self) -> 'None':

        index = 0

        while self.is_running.is_set():
            index += 1
            sent = time.time()

            try:
                result = self.client.publish(Topic_Name, {'timed_index': index})
            except Exception:
                with self.lock:
                    self.errors.append(time.time())
                time.sleep(ModuleCtx.Error_Pause)
            else:
                with self.lock:
                    self.acknowledged.append((sent, time.time(), result['msg_id']))
                time.sleep(self.interval)

# ################################################################################################################################

    def start(self) -> 'None':
        self.is_running.set()

        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

        self._thread = thread

# ################################################################################################################################

    def stop(self) -> 'None':
        self.is_running.clear()

        if self._thread is not None:
            self._thread.join()

# ################################################################################################################################

    def get_acknowledged_between(self, start:'float', end:'float') -> 'strlist':
        """ Returns each publication whose request was sent and acknowledged within the given times.
        """
        out:'strlist' = []

        with self.lock:
            for sent, acknowledged, msg_id in self.acknowledged:
                if sent >= start and acknowledged <= end:
                    out.append(msg_id)

        return out

# ################################################################################################################################

    def get_latencies_between(self, start:'float', end:'float') -> 'list[float]':
        """ Returns how long each publication sent and acknowledged within the given times took, in seconds, sorted.
        """
        out:'list[float]' = []

        with self.lock:
            for sent, acknowledged, _ in self.acknowledged:
                if sent >= start and acknowledged <= end:
                    out.append(acknowledged - sent)

        out.sort()
        return out

# ################################################################################################################################

    def get_msg_ids(self) -> 'strlist':
        out:'strlist' = []

        with self.lock:
            for _, _, msg_id in self.acknowledged:
                out.append(msg_id)

        return out

# ################################################################################################################################

    def count_errors_after(self, start:'float') -> 'int':
        out = 0

        with self.lock:
            for error_time in self.errors:
                if error_time >= start:
                    out += 1

        return out

# ################################################################################################################################
# ################################################################################################################################
