# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The mark-out of a failed standby under traffic - the standby is stopped gracefully, killed, frozen, or cut off
# from the active node. The active node marks it out, continues alone with every acknowledgment synced locally,
# and admits the standby again once it resumes.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from ha_faults import apply_fault, ModuleCtx as FaultsCtx, remove_fault
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.mark_out')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the fault and while the active node is alone, in seconds
    Traffic_Seconds = 15

    # How long the active node may take to mark the standby out, in seconds
    Mark_Out_Timeout = 60

    # How long the standby may take to join again once it resumes, in seconds
    Rejoin_Timeout = 300

    # The role of an active node without a standby and of a standby in sync
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

    # The faults of the mark-out
    Faults = [FaultsCtx.Fault_Stop, FaultsCtx.Fault_Kill, FaultsCtx.Fault_Pause, FaultsCtx.Fault_Partition]

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_mark_out(ha_pair:'HAEnvironment', fault:'str') -> 'None':
    """ The active node marks out a standby that failed under traffic, keeps acknowledging publications alone
    and admits the standby again once it resumes, with nothing lost and both copies equal.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The standby fails and the active node marks it out ..
    fault_started = apply_fault(standby, fault, [active.ip])
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert not record['standby_in_sync'], record

    # .. and keeps acknowledging publications alone ..
    acknowledged_before = len(workload.acknowledged)
    time.sleep(ModuleCtx.Traffic_Seconds)
    acknowledged_alone = len(workload.acknowledged) - acknowledged_before

    assert acknowledged_alone > 0, 'No publication acknowledged while the active node was alone'

    # .. until the standby resumes and joins again.
    remove_fault(standby, fault)
    workload.fault_windows.append((fault_started, time.time()))

    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
