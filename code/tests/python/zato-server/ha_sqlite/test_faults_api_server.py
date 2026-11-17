# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults on the link between one node and the API server - latency and loss - on the standby that takes over
# and on the active node that marks out its standby, and an outage of the API server during a takeover and an admission.
# A node that cannot reach the referee does not act on its own, at no moment are two nodes active, and the pair recovers
# once the link or the API server does.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
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
    Faults = [Fault_Delay, Fault_Loss]

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

    # Each event with the node whose link is degraded, which is the node that acts on the referee record during it
    Link_Cases = [
        (Event_Takeover, Target_Standby),
        (Event_Mark_Out, Target_Active),
    ]

    # The events during which the API server is unavailable
    Outage_Events = [Event_Takeover, Event_Admission]

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # How many claims of each scheduler job a server killed between a claim and its run may leave without a run
    Unrun_Claims_After_Kill = 1

    # How long the traffic runs before the event and how long the fault lasts after it, in seconds
    Traffic_Seconds = 5
    Fault_Seconds = 15

    # How long the pair may take to recover once the link and the failed node do, in seconds
    Recovery_Timeout = 300

    # How long the active node may take to mark out the standby that failed, in seconds
    Mark_Out_Timeout = 60

    # The roles of the pair
    Active_Solo     = ['ActiveSolo']
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('event, target', ModuleCtx.Link_Cases)
@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_api_server_link(ha_pair:'HAEnvironment', fault:'str', event:'str', target:'str') -> 'None':
    """ With the link to the API server degraded on the node that acts on the referee record, the other node fails,
    no two nodes are active at once, and the pair recovers with nothing lost once the link and the failed node do.
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
    degrade_link(degraded, [TopologyCtx.API_Server_IP], ModuleCtx.Netem[fault])

    fault_started = time.time()
    failed.kill()

    both_active = watch_roles(env, ModuleCtx.Fault_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    # .. then the link and the failed node recover ..
    restore_link(degraded)
    failed.resume()

    # .. and the pair forms again.
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((fault_started, time.time()))

    check_workload(env, workload)

    # An active node that cannot reach the API server when its standby fails cannot mark it out, so it stops its server,
    # and a claim that the barrier held is in its copy without a run. An active node that is killed leaves the claim
    # it committed before the run began in the copy of the standby without a run.
    if target == ModuleCtx.Target_Active and event == ModuleCtx.Event_Mark_Out:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Isolation
    elif event == ModuleCtx.Event_Takeover:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Kill
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
    ModuleCtx.Event_Admission: _outage_during_admission,
}

# ################################################################################################################################

@pytest.mark.parametrize('event', ModuleCtx.Outage_Events)
def test_api_server_outage(ha_pair:'HAEnvironment', event:'str') -> 'None':
    """ With the API server unavailable during a takeover or an admission, no node acts on the referee record,
    no two nodes are active at once, and the pair recovers with nothing lost once the API server returns.
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

    # An active node that is killed leaves the claim it committed before the run began in the copy of the standby
    # without a run.
    if event == ModuleCtx.Event_Takeover:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Kill
    else:
        unrun_claims = 0

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
