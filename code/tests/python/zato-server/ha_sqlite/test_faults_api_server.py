# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults on the link between one node and the API server - latency, loss and a black hole - during a takeover and
# during a mark-out, and an outage of the API server during a takeover, a mark-out and an admission. A node that cannot
# reach the referee does not act on its own, at no moment are two nodes active, and the pair recovers once the link
# or the API server does.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
from ha_faults import heal, partition
from ha_tools import degrade_link, restore_link
from topology import ModuleCtx as TopologyCtx
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.faults_api_server')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the link to the API server
    Fault_Delay = 'delay'
    Fault_Loss = 'loss'
    Fault_Black_Hole = 'black-hole'

    Netem = {
        Fault_Delay: 'delay 500ms 100ms distribution normal',
        Fault_Loss: 'loss 30%',
    }

    # The events during which the link is degraded
    Event_Takeover  = 'takeover'
    Event_Mark_Out  = 'mark-out'
    Event_Admission = 'admission'

    # The node whose link is degraded
    Target_Active = 'active'
    Target_Standby = 'standby'

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # How long the traffic runs before the event and how long the fault lasts after it, in seconds
    Traffic_Seconds = 10
    Fault_Seconds = 30

    # How long the pair may take to recover once the link and the failed node do, in seconds
    Recovery_Timeout = 300

    # How long the active node may take to mark out the standby that failed, in seconds
    Mark_Out_Timeout = 60

    # The roles of the pair
    Active_Solo     = ['ActiveSolo']
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

def _degrade(node:'Node', fault:'str') -> 'None':

    if fault == ModuleCtx.Fault_Black_Hole:
        partition(node, [TopologyCtx.API_Server_IP])
    else:
        degrade_link(node, [TopologyCtx.API_Server_IP], ModuleCtx.Netem[fault])

# ################################################################################################################################

def _restore(node:'Node', fault:'str') -> 'None':

    # A node that was killed starts again with a network namespace of its own, without the fault.
    if not node.is_running():
        return

    if fault == ModuleCtx.Fault_Black_Hole:
        heal(node)
    else:
        restore_link(node)

# ################################################################################################################################

@pytest.mark.parametrize('event', [ModuleCtx.Event_Takeover, ModuleCtx.Event_Mark_Out])
@pytest.mark.parametrize('target', [ModuleCtx.Target_Active, ModuleCtx.Target_Standby])
@pytest.mark.parametrize('fault', [ModuleCtx.Fault_Delay, ModuleCtx.Fault_Loss, ModuleCtx.Fault_Black_Hole])
def test_api_server_link(ha_pair:'HAEnvironment', fault:'str', target:'str', event:'str') -> 'None':
    """ With the link of one node to the API server degraded, the active node or the standby fails, no two nodes are active
    at once, and the pair recovers with nothing lost once the link and the failed node do.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    if target == ModuleCtx.Target_Active:
        degraded = active
    else:
        degraded = standby

    if event == ModuleCtx.Event_Takeover:
        failed = active
    else:
        failed = standby

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The link degrades and a node fails ..
    _degrade(degraded, fault)

    fault_started = time.time()
    failed.kill()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    # .. then the link and the failed node recover ..
    _restore(degraded, fault)
    failed.resume()

    # .. and the pair forms again.
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((fault_started, time.time()))

    check_workload(env, workload)

    # An active node that cannot reach the API server when its standby fails cannot mark it out, so it stops its server,
    # and a claim that the barrier held is in its copy without a run.
    if target == ModuleCtx.Target_Active and event == ModuleCtx.Event_Mark_Out:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Isolation
    else:
        unrun_claims = 0

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################

def _outage_during_takeover(env:'HAEnvironment', active:'Node', standby:'Node') -> 'None':
    """ The active node fails while the API server is unavailable, so the standby cannot take over until it returns.
    """
    env.referee.stop()
    active.kill()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'
    assert not standby.is_active(), 'The standby took over without the referee'

    env.referee.resume()
    active.resume()

# ################################################################################################################################

def _outage_during_mark_out(env:'HAEnvironment', active:'Node', standby:'Node') -> 'None':
    """ The standby fails while the API server is unavailable, so the active node cannot mark it out until it returns.
    """
    env.referee.stop()
    standby.kill()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    env.referee.resume()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)
    standby.resume()

# ################################################################################################################################

def _outage_during_admission(env:'HAEnvironment', active:'Node', standby:'Node') -> 'None':
    """ The standby joins again while the API server is unavailable, so it is not admitted until the API server returns.
    """
    standby.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    env.referee.stop()
    standby.resume()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    report = standby.read_role()
    if report is not None:
        assert report['role'] != ModuleCtx.Standby_In_Sync, f'Admitted without the referee -> {report}'

    env.referee.resume()

# ################################################################################################################################

# What each event of an outage does to the pair
_outages = {
    ModuleCtx.Event_Takeover:  _outage_during_takeover,
    ModuleCtx.Event_Mark_Out:  _outage_during_mark_out,
    ModuleCtx.Event_Admission: _outage_during_admission,
}

# ################################################################################################################################

@pytest.mark.parametrize('event', [ModuleCtx.Event_Takeover, ModuleCtx.Event_Mark_Out, ModuleCtx.Event_Admission])
def test_api_server_outage(ha_pair:'HAEnvironment', event:'str') -> 'None':
    """ With the API server unavailable during a takeover, a mark-out or an admission, no node acts on the referee
    record, no two nodes are active at once, and the pair recovers with nothing lost once the API server returns.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The API server is unavailable while the pair changes ..
    fault_started = time.time()
    outage = _outages[event]
    outage(env, active, standby)

    # .. and the pair forms again once it returns.
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((fault_started, time.time()))

    check_workload(env, workload)

    # An active node that cannot mark out its failed standby stops its server, and a claim that the barrier held
    # is in its copy without a run.
    if event == ModuleCtx.Event_Mark_Out:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Isolation
    else:
        unrun_claims = 0

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
