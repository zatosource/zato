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
from arbiter_common import Condition_Timeout, config_started, is_running, new_config, none_running, Probe, \
    Region_Config, start_arbiter, start_arbiter_process, Starts_Metric, stop_arbiter, wait_until, worker_replaced
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a test observes the respawns of a worker that exits at once, in seconds
_backoff_observation = 1.5

# The bounds of the number of workers started within the observation period
_backoff_starts_min = 3
_backoff_starts_max = 8

# How long the processes have to exit after the arbiter terminated, in seconds
_exit_after_arbiter = 5.0

# ################################################################################################################################
# ################################################################################################################################

def test_the_worker_starts_and_exits_on_stop(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'serve', tmp_dir)

    # The worker runs in its first generation ..
    assert probe.worker_generation() == 1

    # .. and does not remain after the arbiter stops.
    stop_arbiter(arbiter, [probe.worker_pid()], tmp_dir)

# ################################################################################################################################

def test_a_terminated_worker_is_replaced(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'serve', tmp_dir)
    pid = probe.worker_pid()

    # The worker is terminated ..
    os.kill(pid, signal.SIGKILL)

    # .. and a worker of the next generation replaces it.
    assert wait_until(worker_replaced, (probe, 2))

    replacement = probe.worker_pid()
    assert replacement != pid

    stop_arbiter(arbiter, [replacement], tmp_dir)

# ################################################################################################################################

def test_a_worker_without_heartbeats_is_terminated_and_replaced(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'no_heartbeat', tmp_dir)
    pid = probe.worker_pid()

    # The worker that writes no heartbeat is replaced.
    assert wait_until(worker_replaced, (probe, 2))
    assert not is_running(pid)

    stop_arbiter(arbiter, [probe.worker_pid()], tmp_dir)

# ################################################################################################################################

def test_a_worker_that_does_not_start_is_terminated_after_the_startup_timeout(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()

    # The first worker never reports ready ..
    arbiter = start_arbiter_process(region, probe, 'never_ready', tmp_dir)
    assert wait_until(probe.reached, (Starts_Metric, 1))

    # .. it is kept beyond the heartbeat threshold, which applies to a ready worker only ..
    heartbeat_threshold = new_config(tmp_dir).heartbeat_threshold
    time.sleep(heartbeat_threshold)

    assert probe.reached(Starts_Metric, 1)

    # .. and replaced after the startup timeout.
    assert wait_until(worker_replaced, (probe, 2))

    stop_arbiter(arbiter, [probe.worker_pid()], tmp_dir)

# ################################################################################################################################

def test_respawns_of_the_worker_back_off(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()

    # The worker keeps exiting ..
    arbiter = start_arbiter_process(region, probe, 'exit_at_once', tmp_dir)
    assert wait_until(probe.reached, (Starts_Metric, 1))

    time.sleep(_backoff_observation)

    # .. and its respawns are spaced by the growing delay.
    starts = probe.metrics[Starts_Metric]

    assert starts >= _backoff_starts_min
    assert starts <= _backoff_starts_max

    stop_arbiter(arbiter, [], tmp_dir)

# ################################################################################################################################

def test_a_worker_that_does_not_drain_is_terminated_after_the_grace_period(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'ignore_drain', tmp_dir)

    stop_arbiter(arbiter, [probe.worker_pid()], tmp_dir)

# ################################################################################################################################

def test_the_processes_terminate_with_the_arbiter(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'serve_with_config', tmp_dir)

    assert config_started(probe)
    pids = [probe.worker_pid(), probe.config_pid.value]

    # The arbiter is terminated with no chance to stop its processes ..
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
