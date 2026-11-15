# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time

# Zato
from arbiter_common import all_slots_ready, get_pids, Region_Config, Release_Metric, Slot_Count, slot_replaced, \
    start_arbiter_process, stop_arbiter, Tested_Slot, wait_until
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_STARTING, STATE_STOPPED

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# How long a test observes that no other slot starts, in seconds, which is below the startup timeout of the test arbiter
_observation = 0.4

# ################################################################################################################################
# ################################################################################################################################

def _first_slot_starting(region:'SharedRegion', generation:'int') -> 'bool':
    out = region.slot_generation(ArbiterCtx.First_Slot) == generation
    out = out and region.slot_state(ArbiterCtx.First_Slot) == STATE_STARTING
    return out

# ################################################################################################################################

def _release_first_slot(region:'SharedRegion') -> 'None':
    region.metric_add(ArbiterCtx.First_Slot, Release_Metric, 1)

# ################################################################################################################################
# ################################################################################################################################

def test_the_other_slots_start_once_the_first_slot_is_ready(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)
    arbiter = start_arbiter_process(region, 'first_slot_late', tmp_dir)

    # The first slot starts alone ..
    assert wait_until(_first_slot_starting, (region, 1))
    time.sleep(_observation)

    for slot in range(Slot_Count):
        if slot != ArbiterCtx.First_Slot:
            assert region.slot_pid(slot) == 0
            assert region.slot_generation(slot) == 0

    # .. and every other slot receives its worker once the first one is ready.
    _release_first_slot(region)
    assert wait_until(all_slots_ready, (region,))

    pids = get_pids(region)
    stop_arbiter(arbiter, pids, tmp_dir)

# ################################################################################################################################

def test_a_replacement_waits_while_the_first_slot_restarts(tmp_path:'Path') -> 'None':
    tmp_dir = str(tmp_path)
    region = SharedRegion(Region_Config)

    _release_first_slot(region)
    arbiter = start_arbiter_process(region, 'first_slot_late', tmp_dir)
    assert wait_until(all_slots_ready, (region,))

    pids = get_pids(region)

    # The worker of the first slot is terminated, and its next generation starts ..
    os.kill(pids[ArbiterCtx.First_Slot], signal.SIGKILL)
    assert wait_until(_first_slot_starting, (region, 2))

    # .. the worker of another slot is terminated meanwhile, and its slot receives no replacement ..
    os.kill(pids[Tested_Slot], signal.SIGKILL)
    time.sleep(_observation)

    assert region.slot_generation(Tested_Slot) == 1
    assert region.slot_state(Tested_Slot) == STATE_STOPPED

    # .. until the first slot is ready again.
    _release_first_slot(region)

    assert wait_until(slot_replaced, (region, ArbiterCtx.First_Slot, 2))
    assert wait_until(slot_replaced, (region, Tested_Slot, 2))

    current = get_pids(region)
    stop_arbiter(arbiter, current, tmp_dir)

# ################################################################################################################################
# ################################################################################################################################
