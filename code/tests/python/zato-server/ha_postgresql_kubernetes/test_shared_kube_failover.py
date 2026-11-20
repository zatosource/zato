# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The duration of a failover. A client sends a request to the Service of the pair every 10 ms over a keep-alive
# connection while every packet to and from the node of the active pod is dropped. The standby takes over, its server
# starts and raises the generation, its pod is labeled once the server answers, and the client is served again
# within the takeover time, the start of the server and the propagation of the endpoints.

# stdlib
import re
import time

# Zato
from kube_checks import find_moment, get_pair, ModuleCtx as ChecksCtx, read_pod_log, wait_for_ok
from kube_env import ModuleCtx as EnvCtx
from kube_faults import heal_node, isolate_node
from kube_traffic import FailoverClient, ModuleCtx as TrafficCtx, RequestRecord
from nodes import ModuleCtx as NodesCtx
from zato.common.test.ha_limits import HALimits

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from kube_traffic import record_list
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the session of the previous server may be kept once the raise begins, in seconds
    Session_End_Limit = 1.0

    # How long the client may take to be served before the isolation, and after it, in seconds
    Served_Timeout = 120

    # How long the standby may take to report the active role, in seconds
    Takeover_Timeout = 120

    # How long the client keeps sending requests after its first answer from the new active pod, in seconds
    Served_Seconds = 5

    # The roles of a pod that serves requests
    Active_Roles:'strlist' = [NodesCtx.Role_Active]

    # The lines of the node and of the server of the new active pod that the test reads the times of a failover from
    Active_Line = re.compile(r'Active at generation \d+ after ')
    Answer_Line = re.compile(r'Zato server answers at generation \d+')
    Label_Line = 'Pod {} labeled as serving: true'
    Raised_Line = re.compile(r'Pub/sub generation raised -> \d+')
    Ended_Line = re.compile(r'Ended pub/sub sessions of a previous server -> pids:.*, waited:([\d.]+)s')

# ################################################################################################################################
# ################################################################################################################################

def _get_old_connection_request(records:'record_list', isolated_at:'float') -> 'RequestRecord':
    """ Returns the first request after the isolation that the old active pod left unanswered, which the client sent
    over the connection opened before the isolation.
    """
    for record in records:
        if record.sent >= isolated_at:
            if record.outcome != TrafficCtx.Outcome_OK:
                return record

    raise Exception(f'No unanswered request after {isolated_at}')

# ################################################################################################################################
# ################################################################################################################################

def test_failover_duration(kube_pair:'KubeEnvironment') -> 'None':
    """ The node of the active pod stops responding under traffic, and the client is served by the standby again
    within the takeover time, the start of the server and the propagation of the endpoints.
    """
    env = kube_pair
    active, standby = get_pair(env)

    # The client is served by the active pod before the fault ..
    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    client.start()

    try:
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)

        # .. the node of the active pod stops responding. The isolation begins before the rules are applied
        # .. and is complete once the command returns, so the old active pod may still answer in between ..
        isolated_at = isolate_node(active.host_node)
        isolation_complete_at = time.time()

        # .. the standby takes over and its server answers through the Service ..
        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
        first_ok = wait_for_ok(client, isolation_complete_at, ModuleCtx.Served_Timeout)

        # .. and the client keeps being served afterwards.
        time.sleep(ModuleCtx.Served_Seconds)

    # The node is healed before the outcome is checked, so that the output of its pods can be read if the test fails.
    finally:
        client.stop()
        heal_node(active.host_node)

    records = client.get_records()
    entries = read_pod_log(standby.pod_name)

    # The times of the failover from the output of the new active pod
    active_at = find_moment(entries, isolated_at, ModuleCtx.Active_Line, 'the active role')
    answer_at = find_moment(entries, isolated_at, ModuleCtx.Answer_Line, 'the answer of the server')
    label_pattern = re.compile(re.escape(ModuleCtx.Label_Line.format(standby.pod_name)))
    label_at = find_moment(entries, isolated_at, label_pattern, 'the label of the pod')
    raised_at = find_moment(entries, isolated_at, ModuleCtx.Raised_Line, 'the raised generation')
    first_ok_at = first_ok.ended

    timeline = f'isolated:{isolated_at:.3f}, active:{active_at:.3f}, raised:{raised_at:.3f}, answer:{answer_at:.3f}, ' \
        f'label:{label_at:.3f}, first ok:{first_ok_at:.3f}'

    # The pod is labeled only once its server answers ..
    assert label_at >= answer_at, f'Pod labeled before its server answered -> {timeline}'

    # .. no request fails after the first one that the new active pod answered ..
    for record in records:
        if record.sent > first_ok.sent:
            assert record.outcome == TrafficCtx.Outcome_OK, f'Request failed after the first answer -> {record}, {timeline}'

    # .. the request on the connection to the isolated pod ends within the timeout of the client ..
    old_request = _get_old_connection_request(records, isolated_at)
    old_duration = old_request.ended - old_request.sent
    old_limit = TrafficCtx.Client_Timeout + TrafficCtx.Request_Interval
    assert old_duration <= old_limit, f'Request on the old connection took {old_duration:.3f}s -> {old_request}'

    # .. the client is served again within the takeover time, the start of the server and the propagation ..
    outage = first_ok_at - isolated_at
    outage_limit = env.timers.takeover + HALimits.Server_Start + ChecksCtx.Propagation_Limit
    assert outage <= outage_limit, f'Outage of {outage:.3f}s above {outage_limit:.3f}s -> {timeline}'

    # .. and the raise ends the sessions of the previous server without waiting for them.
    for moment, text in entries:
        if moment >= isolated_at:
            if match := ModuleCtx.Ended_Line.search(text):
                waited = float(match.group(1))
                assert waited <= ModuleCtx.Session_End_Limit, f'Sessions ended {waited}s into the raise -> {text}'

# ################################################################################################################################
# ################################################################################################################################
