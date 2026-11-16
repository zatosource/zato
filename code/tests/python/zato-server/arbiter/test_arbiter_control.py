# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from arbiter_common import config_started, Drains_Metric, Event_Count, Events_Metric, Probe, Query_Metric, Region_Config, \
    Reloads_Metric, start_arbiter, stop_arbiter, wait_until
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

def test_the_events_of_the_worker_reach_the_config_process_in_order(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()

    # The worker publishes its events and the config process counts those that arrive in the order of publication ..
    arbiter = start_arbiter(region, probe, 'publish', tmp_dir)

    # .. so every event reaches the config process, in order.
    assert wait_until(probe.reached, (Events_Metric, Event_Count))

    time.sleep(_settle_time)
    assert probe.reached(Events_Metric, Event_Count)

    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

# ################################################################################################################################

def test_a_query_of_the_config_process_returns_the_response_of_the_worker(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()

    # The config process queries the worker once it is ready, and counts the response that carries its process ID.
    arbiter = start_arbiter(region, probe, 'query', tmp_dir)

    assert wait_until(probe.reached, (Query_Metric, 1))

    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

# ################################################################################################################################

def test_an_abnormal_termination_of_the_config_process_makes_the_worker_reload(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()

    # The first config process terminates abnormally once the worker is ready ..
    arbiter = start_arbiter(region, probe, 'exit_config_once', tmp_dir)

    # .. and the worker reloads once, after its replacement reported ready.
    assert wait_until(probe.reached, (Reloads_Metric, 1))

    time.sleep(_settle_time)
    assert probe.reached(Reloads_Metric, 1)

    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

# ################################################################################################################################

def test_both_processes_receive_the_drain_command_on_stop(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'serve_with_config', tmp_dir)

    assert config_started(probe)
    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

    assert probe.reached(Drains_Metric, 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
