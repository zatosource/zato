# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import random
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

# Zato
from pubsub_exactly_once.server import kill_worker
from pubsub_perf.clients import get_lease_wait
from pubsub_perf.scenario import Timing
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_perf.clients import futurelist
    from pubsub_perf.progress import Progress
    from pubsub_perf.scenario import ScenarioRun

    futurelist = futurelist

# ################################################################################################################################
# ################################################################################################################################

floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

# How often the runner looks at the clients and at the queues, in seconds
_poll_seconds = 1.0

# How long everything published may take to reach every subscriber once the publishers stopped, in seconds
_settle_timeout = 1800.0

# The threads of the runner itself - the progress and the killer of the worker
_runner_thread_count = 2

# ################################################################################################################################
# ################################################################################################################################

def new_prefix() -> 'str':
    """ Returns a prefix of the keys unique to one run.
    """
    suffix = CryptoManager.generate_hex_string(8)

    out = f'perf.{suffix}.'
    return out

# ################################################################################################################################

def _raise_failures(futures:'futurelist') -> 'None':
    """ Raises the exception of any thread that failed.
    """
    for future in futures:
        if future.done():
            future.result()

# ################################################################################################################################

def _wait_for(futures:'futurelist', background:'futurelist') -> 'None':
    """ Waits until the threads finish, failing as soon as any of them or of the background threads fails.
    """
    while True:

        _raise_failures(futures)
        _raise_failures(background)

        for future in futures:
            if not future.done():
                break
        else:
            break

        time.sleep(_poll_seconds)

# ################################################################################################################################

def _wait_until_settled(run:'ScenarioRun', background:'futurelist') -> 'None':
    """ Waits until each subscriber processed everything that was published.
    """
    deadline = time.monotonic() + _settle_timeout

    while not run.is_settled():

        _raise_failures(background)

        assert time.monotonic() < deadline, f'Not settled within {_settle_timeout}s'
        time.sleep(_poll_seconds)

# ################################################################################################################################

def _kill_worker_at_random(duration:'float', kill_count:'int') -> 'None':
    """ Kills the worker at random moments within the given number of seconds from now.
    """
    start = time.monotonic()
    kill_times:'floatlist' = []

    for _ in range(kill_count):
        offset = random.uniform(0, duration)
        kill_times.append(offset)

    kill_times.sort()

    for offset in kill_times:
        delay = start + offset - time.monotonic()

        if delay > 0:
            time.sleep(delay)

        kill_worker()

# ################################################################################################################################

def run_scenario(progress:'Progress', run:'ScenarioRun', duration:'float', kill_count:'int') -> 'Timing':
    """ Runs one scenario - the subscribers from the start, the publishers for the given number of seconds
    and the given number of worker kills within that time - and returns once each subscriber processed everything.
    """
    stop = Event()
    progress_stop = Event()

    run.add_progress(progress)
    thread_count = _runner_thread_count + run.thread_count

    with ThreadPoolExecutor(max_workers=thread_count) as executor:

        # The subscribers wait for messages from the start ..
        background = run.submit_subscribers(executor, stop)

        progress_future = executor.submit(progress.run, progress_stop)
        background.append(progress_future)

        # .. the publishers publish until the deadline, with the worker killed meanwhile if requested ..
        start = time.monotonic()
        deadline = start + duration

        foreground = run.submit_publishers(executor, deadline)

        if kill_count:
            killer_future = executor.submit(_kill_worker_at_random, duration, kill_count)
            foreground.append(killer_future)

        try:
            _wait_for(foreground, background)
            published_at = time.monotonic()

            # .. each subscriber processes everything published ..
            _wait_until_settled(run, background)
            settled_at = time.monotonic()

            # .. and the subscribers keep pulling for one more lease, in which a message handed out again would arrive.
            time.sleep(get_lease_wait())

        finally:
            stop.set()
            progress_stop.set()

        for future in background:
            future.result()

    out = Timing(start, published_at, settled_at)
    return out

# ################################################################################################################################
# ################################################################################################################################
