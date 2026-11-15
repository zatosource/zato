# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal

# Zato
from arbiter_common import get_pids, Lock_Metric, Lock_Sub_Key, metric_reached, Region_Config, start_arbiter, stop_arbiter, \
    Tested_Slot, wait_until, Waiting_Slot, Writes_Metric
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
    arbiter = start_arbiter(region, 'hold_publish_lock', tmp_dir)
    pids = get_pids(region)

    entry = region.lock_entry(Lock_Sub_Key)

    # One worker holds the publish lock of the queue while the worker of another slot waits for it ..
    assert wait_until(metric_reached, (region, Lock_Metric, 1))
    assert wait_until(region.lock_has_place, (entry, Waiting_Slot))
    assert not metric_reached(region, Writes_Metric, 1)

    # .. the holder is terminated ..
    holder_pid = pids[Tested_Slot]
    os.kill(holder_pid, signal.SIGKILL)

    # .. and the waiting worker publishes once the arbiter withdrew the ticket of the holder and woke it.
    assert wait_until(metric_reached, (region, Writes_Metric, 1))
    assert not region.lock_has_place(entry, Tested_Slot)

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
