# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from multiprocessing import get_context

# gevent
import gevent
from gevent.socket import wait_read

# Zato
from zato.common.pubsub.sql.core import SQLBackendCore
from zato.common.pubsub.sql.wakes import CrossWorkerWakes
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The workers of another process are forked, so that they inherit the region and its descriptors
_context = get_context('fork')

_region_config = {
    'slot_count': 2,
    'wake_capacity': 8,
    'cell_capacity': 8,
    'queue_count': 1,
    'metric_count': 2,
    'series_capacity': 0,
    'series_key_bytes': 0,
    'dedup_capacity': 0,
    'breaker_capacity': 0,
    'lock_capacity': 0,
    'start_id': 1,
}

_publishing_slot = 0
_receiving_slot = 1

# The metrics through which the forked worker reports that it observes its key and that its subscriber woke up
_observing_metric = 0
_woken_metric = 1

_first_key = 'sk-1'
_second_key = 'sk-2'

# How long a test waits for a wake-up, and how often it reads the region meanwhile, in seconds
_timeout = 10.0
_interval = 0.01

# ################################################################################################################################
# ################################################################################################################################

def _ignore_changes(_sub_keys:'strlist') -> 'None':
    """ A test that calls receive itself acts upon the changed keys that it returns.
    """

# ################################################################################################################################

def _wait_for_metric(region:'SharedRegion', metric:'int', value:'int') -> 'bool':
    deadline = time.monotonic() + _timeout

    out = region.metric_sum(metric) == value

    while not out:
        if time.monotonic() >= deadline:
            break

        time.sleep(_interval)
        out = region.metric_sum(metric) == value

    return out

# ################################################################################################################################

def _receive_in_forked_worker(region:'SharedRegion') -> 'None':
    """ Observes one key from the slot of the receiving worker and reports once a publication of another worker woke it.
    """
    exit_code = 1

    try:
        wakes = CrossWorkerWakes(region, _receiving_slot, _ignore_changes)
        wakes.observe(_first_key)

        region.metric_add(_receiving_slot, _observing_metric, 1)

        wake_fd = region.wake_fd(_receiving_slot)
        sub_keys:'strlist' = []

        while not sub_keys:
            wait_read(wake_fd, timeout=_timeout)
            sub_keys = wakes.receive()

        if sub_keys == [_first_key]:
            region.metric_add(_receiving_slot, _woken_metric, 1)
            exit_code = 0

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_a_changed_counter_is_acted_upon_once() -> 'None':
    region = SharedRegion(_region_config)

    publisher = CrossWorkerWakes(region, _publishing_slot, _ignore_changes)
    receiver = CrossWorkerWakes(region, _receiving_slot, _ignore_changes)

    receiver.observe(_first_key)
    receiver.observe(_second_key)

    # A publication changes the counter of its key alone ..
    publisher.publish([_first_key])

    assert receiver.receive() == [_first_key]

    # .. the next read finds no change ..
    assert receiver.receive() == []

    # .. and a publication that follows the read is received in turn.
    publisher.publish([_second_key])

    assert receiver.receive() == [_second_key]

# ################################################################################################################################

def _wake_another_backend() -> 'None':
    """ Runs two backends in a forked process, so that the threads which a backend starts remain in that process
    and no process that a later test forks inherits them.
    """
    gevent.reinit()

    region = SharedRegion(_region_config)

    publishing_backend = SQLBackendCore()
    receiving_backend = SQLBackendCore()

    publishing_backend.start_cross_worker_wakes(region, _publishing_slot)

    # A subscriber that waits before the wake-ups start is observed from their start ..
    first_event = receiving_backend.get_sub_event(_first_key)
    receiving_backend.start_cross_worker_wakes(region, _receiving_slot)

    # .. and one that waits after their start is observed from its first wait ..
    second_event = receiving_backend.get_sub_event(_second_key)

    # .. a publication through the other backend wakes the subscriber of its key and no other ..
    publishing_backend.notify_sub_keys([_first_key])

    assert first_event.wait(_timeout)
    assert not second_event.is_set()

    # .. and a new writer makes each backend wake its subscribers in every backend.
    first_event.clear()
    receiving_backend.on_writer_reconnect()

    assert first_event.wait(_timeout)
    assert second_event.wait(_timeout)

    assert publishing_backend.get_sub_event(_first_key).wait(_timeout)

# ################################################################################################################################

def test_a_publication_wakes_the_subscriber_of_another_backend() -> 'None':
    process = _context.Process(target=_wake_another_backend)
    process.start()
    process.join(_timeout)

    assert process.exitcode == 0

# ################################################################################################################################

def test_a_publication_wakes_the_subscriber_of_another_process() -> 'None':
    region = SharedRegion(_region_config)

    process = _context.Process(target=_receive_in_forked_worker, args=(region,))
    process.start()

    # The publication follows the observation of the key in the other process ..
    assert _wait_for_metric(region, _observing_metric, 1)

    publisher = CrossWorkerWakes(region, _publishing_slot, _ignore_changes)
    publisher.publish([_first_key])

    # .. which receives it through its own descriptor.
    process.join(_timeout)

    assert process.exitcode == 0
    assert region.metric_sum(_woken_metric) == 1

# ################################################################################################################################
# ################################################################################################################################
