# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The loss of the etcd leader of a cluster of three control-plane nodes during a takeover, a mark-out and an admission.
# The node of the leader is frozen, the other two members elect a new leader, and the API servers on their nodes
# serve the lease again, so the pair completes the event, at no moment are two nodes active, and nothing acknowledged
# is lost once the frozen node returns.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
from ha_takeover import ModuleCtx as TakeoverCtx
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from topology import Lease
    from zato.common.typing_ import any_

    any_ = any_
    Lease = Lease

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_control_plane.etcd_leader')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The events during which the etcd leader is lost
    Event_Takeover  = 'takeover'
    Event_Mark_Out  = 'mark-out'
    Event_Admission = 'admission'

    # How long the traffic runs before the event and how long the roles are watched after it, in seconds
    Traffic_Seconds = 10
    Watch_Seconds = 30

    # How long the active node may take to mark out the standby, including the election of a new etcd leader, in seconds
    Mark_Out_Timeout = 60

    # How long the pair may take to form again once the frozen node returns, in seconds
    Recovery_Timeout = 300

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # How many claims of each scheduler job a server killed between a claim and its run may leave without a run
    Unrun_Claims_After_Kill = 1

    # The roles of the pair
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _leader_lost_during_takeover(env:'HAEnvironment', lease:'Lease', active:'Node', standby:'Node') -> 'None':
    """ The active node fails while the etcd leader is lost, and the standby takes over through the new leader.
    """
    leader = lease.find_etcd_leader()
    lease.freeze_control_plane(leader)
    active.kill()

    _ = standby.wait_for_role(TakeoverCtx.Active_Roles, TakeoverCtx.Takeover_Timeout)
    _ = standby.wait_until_server_up(TakeoverCtx.Server_Timeout)

    both_active = watch_roles(env, ModuleCtx.Watch_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    lease.thaw_control_plane(leader)
    active.resume()

# ################################################################################################################################

def _leader_lost_during_mark_out(env:'HAEnvironment', lease:'Lease', active:'Node', standby:'Node') -> 'None':
    """ The standby fails while the etcd leader is lost, and the active node marks it out through the new leader.
    """
    leader = lease.find_etcd_leader()
    lease.freeze_control_plane(leader)
    standby.kill()

    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    both_active = watch_roles(env, ModuleCtx.Watch_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    lease.thaw_control_plane(leader)
    standby.resume()

# ################################################################################################################################

def _leader_lost_during_admission(env:'HAEnvironment', lease:'Lease', active:'Node', standby:'Node') -> 'None':
    """ The standby joins again while the etcd leader is lost, and the active node admits it through the new leader.
    """
    standby.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    leader = lease.find_etcd_leader()
    lease.freeze_control_plane(leader)
    standby.resume()

    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, TakeoverCtx.Rejoin_Timeout)

    both_active = watch_roles(env, ModuleCtx.Watch_Seconds)
    assert not both_active, f'Two active nodes -> {both_active}'

    lease.thaw_control_plane(leader)

# ################################################################################################################################

# What the loss of the etcd leader during each event does to the pair
_events = {
    ModuleCtx.Event_Takeover:  _leader_lost_during_takeover,
    ModuleCtx.Event_Mark_Out:  _leader_lost_during_mark_out,
    ModuleCtx.Event_Admission: _leader_lost_during_admission,
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('event', [ModuleCtx.Event_Takeover, ModuleCtx.Event_Mark_Out, ModuleCtx.Event_Admission])
def test_etcd_leader_lost(ha_pair:'HAEnvironment', event:'str') -> 'None':
    """ With the etcd leader lost during a takeover, a mark-out or an admission, the pair completes the event through
    the new leader, no two nodes are active at once, and nothing acknowledged is lost.
    """
    env = ha_pair
    lease = cast_('Lease', env.referee)

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The etcd leader is lost while the pair changes ..
    fault_started = time.time()
    run_event = _events[event]
    run_event(env, lease, active, standby)

    # .. and the pair forms again once the frozen node returns.
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    workload.fault_windows.append((fault_started, time.time()))

    check_workload(env, workload)

    # An active node whose referee answers too late when its standby fails stops its server, and a claim
    # that the barrier held is in its copy without a run. An active node that is killed leaves the claim it committed
    # before the run began in the copy of the standby without a run.
    if event == ModuleCtx.Event_Mark_Out:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Isolation
    elif event == ModuleCtx.Event_Takeover:
        unrun_claims = ModuleCtx.Unrun_Claims_After_Kill
    else:
        unrun_claims = 0

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
