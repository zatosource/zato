# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal

# Zato
from arbiter_common import Lock_Metric, Lock_Sub_Key, Probe, Region_Config, start_arbiter, stop_arbiter, wait_until, \
    worker_replaced, Writes_Metric
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def test_the_publish_lock_of_a_terminated_worker_passes_on(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    probe = Probe()
    arbiter = start_arbiter(region, probe, 'hold_publish_lock', tmp_dir)
    pid = probe.worker_pid()

    entry = region.lock_entry(Lock_Sub_Key)

    # The worker holds the publish lock of the queue while the config process waits for it ..
    assert wait_until(probe.reached, (Lock_Metric, 1))
    assert wait_until(region.lock_has_place, (entry, region.config_place))
    assert not probe.reached(Writes_Metric, 1)

    # .. the worker is terminated ..
    os.kill(pid, signal.SIGKILL)

    # .. and the config process publishes once the arbiter withdrew the ticket of the worker and woke it.
    assert wait_until(probe.reached, (Writes_Metric, 1))
    assert not region.lock_has_place(entry, region.worker_place)

    assert wait_until(worker_replaced, (probe, 2))
    stop_arbiter(arbiter, [probe.worker_pid(), probe.config_pid.value], tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
