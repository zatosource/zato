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
from arbiter_common import Condition_Timeout, get_pids, is_running, metric_reached, new_config, none_running, Queue, \
    Region_Config, Slot_Count, slot_replaced, start_arbiter, start_arbiter_process, stop_arbiter, Tested_Slot, wait_until, \
    Waiting_Slot, Writes_Metric
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a test observes the respawns of a slot whose workers exit at once, in seconds
_backoff_observation = 1.5

# The bounds of the generations of that slot within the observation period
_backoff_generations_min = 3
_backoff_generations_max = 8

# How long the workers have to exit after the arbiter terminated, in seconds
_exit_after_arbiter = 5.0

# ################################################################################################################################
# ################################################################################################################################

def test_every_slot_receives_a_worker_and_every_worker_exits_on_stop(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', tmp_dir)

    # Each slot has a worker of its own, in its first generation ..
    pids = get_pids(region)
    unique_pids = set(pids)

    assert len(unique_pids) == Slot_Count

    for slot in range(Slot_Count):
        assert region.slot_generation(slot) == 1

    # .. and none remains after the arbiter stops.
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_a_terminated_worker_is_replaced_in_its_slot(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'serve', tmp_dir)
    pids = get_pids(region)

    # The worker of one slot is terminated ..
    tested_pid = pids[Tested_Slot]
    os.kill(tested_pid, signal.SIGKILL)

    # .. a worker of the next generation takes its slot ..
    assert wait_until(slot_replaced, (region, Tested_Slot, 2))
    replacement = region.slot_pid(Tested_Slot)

    assert replacement not in pids

    # .. and the workers of the other slots are the same.
    for slot in range(Slot_Count):
        if slot != Tested_Slot:
            assert region.slot_pid(slot) == pids[slot]
            assert region.slot_generation(slot) == 1

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_the_place_of_a_terminated_worker_is_withdrawn(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'hold_turn', tmp_dir)
    pids = get_pids(region)

    # One worker holds the turn of the queue while another waits for it ..
    assert wait_until(region.queue_has_place, (Queue, Waiting_Slot))
    assert not metric_reached(region, Writes_Metric, 1)

    # .. the holder is terminated ..
    holder_pid = pids[Tested_Slot]
    os.kill(holder_pid, signal.SIGKILL)

    # .. and the waiting worker makes its write once the arbiter withdrew the place of the holder.
    assert wait_until(metric_reached, (region, Writes_Metric, 1))

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_a_worker_without_heartbeats_is_terminated_and_replaced(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'no_heartbeat', tmp_dir)
    pids = get_pids(region)

    # The worker that writes no heartbeat is replaced ..
    assert wait_until(slot_replaced, (region, Tested_Slot, 2))

    tested_pid = pids[Tested_Slot]
    assert not is_running(tested_pid)

    # .. and the others, whose heartbeats continue, are not.
    for slot in range(Slot_Count):
        if slot != Tested_Slot:
            assert region.slot_pid(slot) == pids[slot]

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_a_worker_that_does_not_start_is_terminated_after_the_startup_timeout(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    # The worker of the tested slot never reports ready, while the others do ..
    arbiter = start_arbiter_process(region, 'never_ready', tmp_dir)

    for slot in range(Slot_Count):
        if slot != Tested_Slot:
            assert wait_until(slot_replaced, (region, slot, 1))

    pids = get_pids(region)

    # .. it is kept beyond the heartbeat threshold, which applies to ready workers only ..
    heartbeat_threshold = new_config(tmp_dir).heartbeat_threshold
    time.sleep(heartbeat_threshold)

    assert region.slot_generation(Tested_Slot) == 1

    # .. and replaced after the startup timeout.
    assert wait_until(slot_replaced, (region, Tested_Slot, 2))

    tested_pid = pids[Tested_Slot]
    assert not is_running(tested_pid)

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_respawns_of_one_slot_back_off_while_the_others_serve(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    # The other slots are ready while the tested one keeps exiting ..
    arbiter = start_arbiter_process(region, 'exit_at_once', tmp_dir)

    for slot in range(Slot_Count):
        if slot != Tested_Slot:
            assert wait_until(slot_replaced, (region, slot, 1))

    pids = get_pids(region)
    time.sleep(_backoff_observation)

    # .. its respawns are spaced by the growing delay ..
    generation = region.slot_generation(Tested_Slot)

    assert generation >= _backoff_generations_min
    assert generation <= _backoff_generations_max

    # .. and the other slots keep their first workers.
    for slot in range(Slot_Count):
        if slot != Tested_Slot:
            assert region.slot_pid(slot) == pids[slot]
            assert region.slot_generation(slot) == 1

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################

def test_a_worker_that_does_not_drain_is_terminated_after_the_grace_period(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'ignore_drain', tmp_dir)
    pids = get_pids(region)

    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_the_workers_terminate_with_the_arbiter(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter(region, 'ignore_drain', tmp_dir)
    pids = get_pids(region)

    # The arbiter is terminated with no chance to stop its workers ..
    os.kill(arbiter.pid, signal.SIGKILL)
    arbiter.join(Condition_Timeout)

    # .. and the kernel terminates them.
    assert wait_until(none_running, (pids,), _exit_after_arbiter)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
