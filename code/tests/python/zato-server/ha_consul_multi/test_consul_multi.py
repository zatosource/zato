# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults of the Consul cluster under traffic during a takeover, a mark-out and an admission. The leader is killed,
# paused and resumed, or partitioned from the other servers while it reaches the nodes, one follower is lost, or two
# followers are lost with the quorum. At no moment are two nodes active, and the pair recovers with nothing lost
# once the cluster and the failed node do.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from consul_multi_env import get_cluster
from consul_multi_faults import apply_cluster_fault, ModuleCtx as FaultsCtx, remove_cluster_fault
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
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

logger = logging.getLogger('zato.test.ha_consul_multi.cluster_faults')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The events of the pair during which the cluster fails
    Event_Takeover = 'takeover'
    Event_Mark_Out = 'mark-out'
    Event_Admission = 'admission'

    Events = [Event_Takeover, Event_Mark_Out, Event_Admission]

    # How long the traffic runs before the event and how long the fault lasts after it, in seconds
    Traffic_Seconds = 10
    Fault_Seconds = 30

    # How long the active node may take to mark out a standby that failed before an admission, in seconds
    Mark_Out_Timeout = 60

    # How long the pair may take to recover once the cluster and the failed node do, in seconds
    Recovery_Timeout = 300

    # The role of an active node without a standby
    Active_Solo = ['ActiveSolo']

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('event', ModuleCtx.Events)
@pytest.mark.parametrize('fault', FaultsCtx.Faults)
def test_consul_cluster_fault(ha_pair:'HAEnvironment', fault:'str', event:'str') -> 'None':
    """ The Consul cluster fails under traffic while the active node fails, while the standby fails, or while
    a standby that failed earlier starts again. No two nodes are active at once, and the pair recovers
    with nothing lost once the cluster and the failed node do.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    fault_started = time.time()

    # Before an admission, the standby fails and the active node marks it out ..
    if event == ModuleCtx.Event_Admission:
        standby.kill()
        _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    # .. the cluster fails ..
    servers, _ = apply_cluster_fault(cluster, fault)

    # .. and during the fault, the active node fails, the standby fails, or the standby starts again.
    if event == ModuleCtx.Event_Takeover:
        failed = active
        failed.kill()

    elif event == ModuleCtx.Event_Mark_Out:
        failed = standby
        failed.kill()

    else:
        failed = standby
        failed.resume()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    # The cluster and the failed node recover ..
    remove_cluster_fault(cluster, fault, servers)

    if event != ModuleCtx.Event_Admission:
        failed.resume()

    # .. and the pair forms again.
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((fault_started, time.time()))

    check_workload(env, workload)

    # An active node that cannot write the mark-out of its standby stops its server, and a claim that the barrier
    # held is in its copy without a run.
    if event == ModuleCtx.Event_Mark_Out:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Isolation
    else:
        unrun_claims = 0

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
