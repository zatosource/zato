# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import sleep

# pytest
import pytest

# Zato
from zato.common.test.pubsub_replication import proxy_command

# local
from checks import check_counts_equal_rows, check_delivery, read_generation
from environment import replicated_environment
from workload import Workload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_replication import ReplicatedDatabase

# ################################################################################################################################
# ################################################################################################################################

# How long the traffic runs before the fault and after it, and how long the backlog may take to drain, in seconds.
_traffic_before_seconds = 5
_traffic_after_seconds = 10
_drain_timeout = 300

# How many messages one pull hands out at most, which bounds what a pull whose response was lost takes along.
_pull_max_messages = 100

# How long each fault lasts, in seconds, the latency added to each direction of the link, in milliseconds,
# and how many times the connections are reset, with the pause between two resets, in seconds.
_fault_seconds = 20
_latency_ms = 50
_reset_count = 5
_reset_pause = 2

# ################################################################################################################################
# ################################################################################################################################

def _inject_latency(database:'ReplicatedDatabase') -> 'None':
    _ = proxy_command(database, f'latency/{_latency_ms}')
    sleep(_fault_seconds)
    _ = proxy_command(database, 'latency/0')

# ################################################################################################################################

def _inject_resets(database:'ReplicatedDatabase') -> 'None':
    for _ in range(_reset_count):
        _ = proxy_command(database, 'reset')
        sleep(_reset_pause)

# ################################################################################################################################

def _inject_refusal(database:'ReplicatedDatabase') -> 'None':
    _ = proxy_command(database, 'block')
    sleep(_fault_seconds)
    _ = proxy_command(database, 'unblock')

# ################################################################################################################################

def _inject_half_open(database:'ReplicatedDatabase') -> 'None':
    _ = proxy_command(database, 'hold')
    sleep(_fault_seconds)
    _ = proxy_command(database, 'release')

# ################################################################################################################################

_faults = {
    'latency': _inject_latency,
    'reset': _inject_resets,
    'refusal': _inject_refusal,
    'half_open': _inject_half_open,
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault_name', sorted(_faults))
def test_network_fault(fault_name:'str') -> 'None':
    """ A fault of the link between the server and the database during traffic loses nothing acknowledged,
    hands no pull out twice, and every component resumes once the link is restored.
    """
    label = f'network.{fault_name}'

    with replicated_environment(fault_name.replace('_', '-'), True) as database:

        workload = Workload(label)
        workload.backend.take_over()

        guard = workload.backend.generation_guard
        assert guard is not None

        workload.subscribe()
        workload.start()

        sleep(_traffic_before_seconds)

        # The fault lasts for a while in the middle of the traffic ..
        fault_time = monotonic()
        _faults[fault_name](database)
        restore_time = monotonic()

        sleep(_traffic_after_seconds)
        workload.stop_publishing()

        # .. each pull whose response was lost may have taken at most one batch along ..
        failed_pulls = 0
        for failed_time in workload.failed_pull_times:
            if failed_time >= fault_time - 1:
                failed_pulls += 1

        workload.wait_until_delivered(_drain_timeout, failed_pulls * _pull_max_messages, set())
        workload.stop()

        measurements = check_delivery(database, workload, restore_time)
        print(f'\nNetwork fault {fault_name} -> {measurements}')

        # .. nothing acknowledged was lost ..
        assert measurements['lost'] == 0, measurements

        # .. every component resumed ..
        for name in ('publish_resumed_after', 'pull_resumed_after', 'push_resumed_after', 'cleanup_resumed_after'):
            assert measurements[name] >= 0, measurements

        check_counts_equal_rows(database, workload)

        # .. and the server is still the active one.
        assert read_generation(database) == guard.generation
        assert not workload.backend.is_replaced

        guard.uninstall(workload.backend.engine)

# ################################################################################################################################
# ################################################################################################################################
