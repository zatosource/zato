# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The failover from a Zato server that no longer works while its node does. A client sends a request to the Service
# of the pair every 10 ms. The server of the active pod is frozen, or its configuration is made unreadable and the server
# is killed, so that each next start exits at once. The node of the active pod finds the server failed and resigns,
# the standby takes over, its pod is labeled once its server answers, and the client is served again.

# stdlib
import re
import time

# pytest
import pytest

# Zato
from kube_checks import find_moment, get_pair, read_pod_log, wait_for_ok
from kube_env import ModuleCtx as EnvCtx
from kube_faults import break_server_config, count_server_processes, freeze_server, kill_server, \
    ModuleCtx as FaultsCtx, restore_server_config, thaw_server
from kube_traffic import FailoverClient
from zato.common.test.ha_limits import HALimits

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment, KubeNode
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the endpoints of the Service may take to follow the label of the new active pod, in seconds
    Propagation_Limit = 2.0

    # How long the client may take to be served before the fault, in seconds
    Served_Timeout = 120

    # How long a wait for the takeover or for the answer of the new active pod exceeds the limit of the test, in seconds,
    # so that an outage above the limit is measured rather than ended by the timeout of the wait
    Wait_Margin = 30.0

    # How long the node of the old active pod may take to stop its server once it resigned, in seconds,
    # which spans the time that the node gives a stopping server before SIGKILL
    Server_Stop_Timeout = 30.0

    # How often the processes of the server of the old active pod are counted while the test waits for their end, in seconds
    Poll_Interval = 0.5

    # How long the old active pod is watched after its configuration is restored, in seconds, a quarter of the hold-off
    # of the node that resigned, which the earlier steps of the test do not use up
    Hold_Off_Watch = EnvCtx.Resign_Hold_Off / 4

    # The roles of a pod that serves requests and of one that waits
    Active_Roles:'strlist' = [EnvCtx.Role_Active]
    Standby_Roles:'strlist' = [EnvCtx.Role_Standby]

    # The lines of the node of each pod that the test reads the times of a failover from
    Resigned_Line = re.compile(r'Resigned the active role at generation \d+ because ')
    Label_Line = 'Pod {} labeled as serving: true'

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server_end(pod:'KubeNode') -> 'None':
    """ Waits until no process of the Zato server runs in a pod.
    """
    deadline = time.monotonic() + ModuleCtx.Server_Stop_Timeout

    while time.monotonic() < deadline:
        if count_server_processes(pod.pod_name) == 0:
            return
        time.sleep(ModuleCtx.Poll_Interval)

    raise Exception(f'Server of {pod.pod_name} still runs {ModuleCtx.Server_Stop_Timeout}s after its node resigned')

# ################################################################################################################################

def _check_label_moved(old_active:'KubeNode', new_active:'KubeNode', fault_at:'float') -> 'str':
    """ Checks that the node of the old active pod resigned and that the new active pod was labeled only afterwards,
    and returns the timeline of both.
    """
    old_entries = read_pod_log(old_active.pod_name)
    new_entries = read_pod_log(new_active.pod_name)

    resigned_at = find_moment(old_entries, fault_at, ModuleCtx.Resigned_Line, 'the resignation')
    label_pattern = re.compile(re.escape(ModuleCtx.Label_Line.format(new_active.pod_name)))
    label_at = find_moment(new_entries, fault_at, label_pattern, 'the label of the new active pod')

    out = f'fault:{fault_at:.3f}, resigned:{resigned_at:.3f}, label:{label_at:.3f}'

    assert label_at >= resigned_at, f'New active pod labeled before the old one resigned -> {out}'

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('scope', [FaultsCtx.Scope_Group, FaultsCtx.Scope_Worker])
def test_hung_server_fails_over(kube_pair:'KubeEnvironment', scope:'str') -> 'None':
    """ The server of the active pod stops answering while its node runs, and the standby takes over within
    the liveness timeout with the ping in progress, the takeover time, the start of the server and the propagation
    of the endpoints.
    """
    env = kube_pair
    active, standby = get_pair(env)

    # The node reads the verdict of the liveness timeout only after the ping in progress returns,
    # so the resignation follows the timeout by up to one ping timeout.
    resign_limit = HALimits.Server_Liveness_Timeout + HALimits.Server_Ping_Timeout

    outage_limit = resign_limit + env.timers.takeover + HALimits.Server_Start + ModuleCtx.Propagation_Limit
    wait_timeout = outage_limit + ModuleCtx.Wait_Margin

    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    client.start()

    try:
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)

        # The server of the active pod is frozen while its node keeps running ..
        frozen_at = freeze_server(active.pod_name, scope)

        # .. the standby takes over and its server answers through the Service. A request that reached the frozen
        # worker is answered by the old server once its node stops it, so only a request sent after the takeover
        # is an answer of the new active pod ..
        _ = standby.wait_for_role(ModuleCtx.Active_Roles, wait_timeout)
        promoted_at = time.time()
        first_ok = wait_for_ok(client, promoted_at, wait_timeout)

        # .. and the node of the old active pod is the standby and has stopped the frozen server itself.
        _ = active.wait_for_role(ModuleCtx.Standby_Roles, wait_timeout)
        _wait_for_server_end(active)

    finally:
        client.stop()
        thaw_server(active.pod_name)

    timeline = _check_label_moved(active, standby, frozen_at)
    timeline += f', first ok:{first_ok.ended:.3f}'

    outage = first_ok.ended - frozen_at
    assert outage <= outage_limit, f'Outage of {outage:.3f}s above {outage_limit:.3f}s -> {timeline}'

# ################################################################################################################################

def test_exiting_server_fails_over(kube_pair:'KubeEnvironment') -> 'None':
    """ The server of the active pod exits at every start, and the standby takes over within the exits of the limit,
    the takeover time, the start of the server and the propagation of the endpoints. The node that resigned
    remains the standby once the server could start again.
    """
    env = kube_pair
    active, standby = get_pair(env)

    exits_limit = HALimits.Server_Exit_Limit * HALimits.Server_Bad_Start
    outage_limit = exits_limit + env.timers.takeover + HALimits.Server_Start + ModuleCtx.Propagation_Limit
    wait_timeout = outage_limit + ModuleCtx.Wait_Margin

    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    client.start()

    try:
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)
        mode = break_server_config(active.pod_name)

        try:

            # The server of the active pod is killed, and each start of it that its node makes exits at once ..
            killed_at = kill_server(active.pod_name)

            # .. the standby takes over and its server answers through the Service ..
            _ = standby.wait_for_role(ModuleCtx.Active_Roles, wait_timeout)
            first_ok = wait_for_ok(client, killed_at, wait_timeout)

            # .. and the node of the old active pod is the standby with no server.
            _ = active.wait_for_role(ModuleCtx.Standby_Roles, wait_timeout)
            _wait_for_server_end(active)

        finally:
            restore_server_config(active.pod_name, mode)

        # The node that resigned stays the standby within its hold-off, although its server could start again,
        # and the pair answers through the new active pod.
        restored_at = time.time()
        time.sleep(ModuleCtx.Hold_Off_Watch)

        report = active.read_role()
        assert report is not None, f'Role endpoint of {active.pod_name} does not answer'
        assert report['role'] in ModuleCtx.Standby_Roles, f'Old active pod not the standby after the restore -> {report}'

        _ = wait_for_ok(client, restored_at, ModuleCtx.Served_Timeout)

    finally:
        client.stop()

    timeline = _check_label_moved(active, standby, killed_at)
    timeline += f', first ok:{first_ok.ended:.3f}'

    outage = first_ok.ended - killed_at
    assert outage <= outage_limit, f'Outage of {outage:.3f}s above {outage_limit:.3f}s -> {timeline}'

# ################################################################################################################################
# ################################################################################################################################
