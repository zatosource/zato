# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time

# pytest
import pytest

# Zato
from arbiter_common import Drains_Metric, Event_Count, Events_Metric, get_pids, metric_reached, Query_Metric, Region_Config, \
    Reloads_Metric, Slot_Count, slot_replaced, start_arbiter, start_arbiter_process, stop_arbiter, Tested_Slot, wait_until
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a test confirms that a count does not grow past its value, in seconds
_settle_time = 0.5

# ################################################################################################################################
# ################################################################################################################################

def test_events_reach_every_other_worker_in_order_including_a_starting_one(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    # The tested slot publishes its events, one slot reports ready only after the other received every event,
    # and each slot counts the events that arrive in the order of publication ..
    arbiter = start_arbiter_process(region, 'publish', tmp_dir)

    other_slots = Slot_Count - 1
    expected = Event_Count * other_slots

    # .. so every event reaches every slot other than its origin, the late one from the startup buffer, in order.
    assert wait_until(metric_reached, (region, Events_Metric, expected))

    time.sleep(_settle_time)
    assert metric_reached(region, Events_Metric, expected)

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_a_query_returns_the_response_of_every_worker(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    # The tested slot queries every worker once all of them are ready, and counts the responses
    # that carry the process ID of their slot, its own response included.
    arbiter = start_arbiter(region, 'query', tmp_dir)

    assert wait_until(metric_reached, (region, Query_Metric, Slot_Count))

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_an_abnormal_termination_makes_every_other_worker_reload(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', tmp_dir)
    pids = get_pids(region)

    # The worker of one slot is terminated ..
    tested_pid = pids[Tested_Slot]
    os.kill(tested_pid, signal.SIGKILL)

    assert wait_until(slot_replaced, (region, Tested_Slot, 2))

    # .. and each of the other workers reloads once, while the replacement loads its configuration at startup.
    other_slots = Slot_Count - 1
    assert wait_until(metric_reached, (region, Reloads_Metric, other_slots))

    time.sleep(_settle_time)
    assert metric_reached(region, Reloads_Metric, other_slots)

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_every_worker_receives_the_drain_command_on_stop(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', tmp_dir)
    pids = get_pids(region)

    stop_arbiter(arbiter, pids, tmp_dir)

    assert metric_reached(region, Drains_Metric, Slot_Count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
