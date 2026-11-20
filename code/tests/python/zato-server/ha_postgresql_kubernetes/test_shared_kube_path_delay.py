# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A delay on the path of the active pod alone. The traffic of the active pod to the API server or to PostgreSQL is delayed
# while the standby reaches both without a delay. A delay below the request timeout of the node keeps the renewals
# of the lease within the takeover time, so the active pod keeps its role and its server keeps answering. A delay
# above the takeover time stops the renewals, and the standby takes over.

# stdlib
import logging
import time

# Zato
from kube_checks import get_pair, wait_for_ok
from kube_cluster import get_service_ip, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
from kube_faults import delay_pod_traffic, remove_pod_delay
from kube_traffic import FailoverClient, ModuleCtx as TrafficCtx
from zato.common.test.ha_limits import HALimits

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment, KubeNode
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.path_delay')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Service through which the pods reach the API server
    API_Server_Namespace = 'default'
    API_Server_Service   = 'kubernetes'

    # The delays of the traffic of the active pod that the renewals of its lease tolerate, in seconds
    API_Server_Delay = 1.5
    PostgreSQL_Delay = 2.5

    # How many times the takeover time a delay that the renewals tolerate is watched for
    Watch_Takeovers = 5

    # How many times the takeover time the delay is that the renewals do not tolerate
    Beyond_Takeovers = 2

    # How often the referee record is read while a delay is watched, in seconds
    Sample_Interval = 0.5

    # How long the client may take to be served before the fault, in seconds
    Served_Timeout = 120

    # How long the former active pod may take to report a role other than the active one once the delay is removed,
    # in seconds
    Former_Active_Timeout = 120

    # The roles of the pods
    Role_Active  = 'Active'
    Role_Standby = 'Standby'
    Role_Fenced  = 'Fenced'

    # The roles of a former active pod once the other pod took over
    Former_Active_Roles:'strlist' = [Role_Fenced, Role_Standby]

# ################################################################################################################################
# ################################################################################################################################

def _get_api_server_ip() -> 'str':
    out = get_service_ip(ModuleCtx.API_Server_Namespace, ModuleCtx.API_Server_Service)
    return out

# ################################################################################################################################

def _get_postgresql_ip(env:'KubeEnvironment') -> 'str':
    backend = env.session.backends[0]

    out = get_service_ip(ClusterCtx.Namespace, backend.service_name)
    return out

# ################################################################################################################################

def _watch_lease(env:'KubeEnvironment', active:'KubeNode', generation:'int', watch_seconds:'float') -> 'float':
    """ Reads the referee record for the given time, asserts that it names the active pod at its generation throughout,
    and returns the longest interval in which its version did not change.
    """
    started = time.monotonic()
    deadline = started + watch_seconds

    version = ''
    changed_at = started
    out = 0.0

    while True:
        now = time.monotonic()

        if now >= deadline:
            break

        record = env.referee.read_record()
        assert record is not None, 'No referee record'
        assert record['active_node'] == active.pod_name, record
        assert record['generation'] == generation, record

        # A renewal raised the version since the previous read ..
        if record['version'] != version:
            interval = now - changed_at
            out = max(out, interval)

            version = record['version']
            changed_at = now

        time.sleep(ModuleCtx.Sample_Interval)

    # .. and the interval since the last renewal counts too.
    interval = time.monotonic() - changed_at
    out = max(out, interval)

    return out

# ################################################################################################################################

def _check_delay_kept_the_lease(env:'KubeEnvironment', address:'str', delay:'float') -> 'None':
    """ Delays the traffic of the active pod to an address under requests through the Service, and checks that
    the renewals of its lease stay within the takeover time, that the pair keeps its roles and that every request
    is answered.
    """
    active, standby = get_pair(env)

    record = env.referee.read_record()
    assert record is not None, 'No referee record'
    generation = record['generation']

    watch_seconds = env.timers.takeover * ModuleCtx.Watch_Takeovers

    # The client is served by the active pod before the fault ..
    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    client.start()

    try:
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)

        # .. the traffic of the active pod alone to the address is delayed ..
        delayed_at = delay_pod_traffic(active.pod_name, active.host_node, address, delay)

        # .. while its lease is renewed within the takeover time.
        try:
            longest_interval = _watch_lease(env, active, generation, watch_seconds)
        finally:
            remove_pod_delay(active.pod_name, active.host_node)

    finally:
        client.stop()

    logger.info('Longest interval without a renewal under a delay of %ss to %s -> %.3fs', delay, address, longest_interval)

    assert longest_interval < env.timers.takeover, \
        f'No renewal for {longest_interval:.3f}s under a delay of {delay}s to {address}'

    # The pair keeps its roles ..
    active_report = active.read_role()
    assert active_report is not None, f'No role report of {active.pod_name}'
    assert active_report['role'] == ModuleCtx.Role_Active, active_report

    standby_report = standby.read_role()
    assert standby_report is not None, f'No role report of {standby.pod_name}'
    assert standby_report['role'] == ModuleCtx.Role_Standby, standby_report

    # .. and the active pod answered every request during the delay.
    for request_record in client.get_records():
        if request_record.sent >= delayed_at:
            assert request_record.outcome == TrafficCtx.Outcome_OK, f'Request failed during the delay -> {request_record}'

# ################################################################################################################################
# ################################################################################################################################

def test_api_server_delay_keeps_the_lease(kube_pair:'KubeEnvironment') -> 'None':
    """ The traffic of the active pod to the API server is delayed below the request timeout of the node,
    and the active pod keeps its lease and its role.
    """
    env = kube_pair
    address = _get_api_server_ip()

    _check_delay_kept_the_lease(env, address, ModuleCtx.API_Server_Delay)

# ################################################################################################################################

def test_postgresql_delay_keeps_the_lease(kube_pair:'KubeEnvironment') -> 'None':
    """ The traffic of the active pod to PostgreSQL is delayed below the request timeout of the node,
    and the active pod keeps its lease and its role.
    """
    env = kube_pair
    address = _get_postgresql_ip(env)

    _check_delay_kept_the_lease(env, address, ModuleCtx.PostgreSQL_Delay)

# ################################################################################################################################

def test_api_server_delay_beyond_takeover_hands_over(kube_pair:'KubeEnvironment') -> 'None':
    """ The traffic of the active pod to the API server is delayed beyond the takeover time, the standby takes over
    at a higher generation, and the former active pod gives up the active role once the delay is removed.
    """
    env = kube_pair
    active, standby = get_pair(env)

    record = env.referee.read_record()
    assert record is not None, 'No referee record'
    generation = record['generation']

    address = _get_api_server_ip()
    delay = env.timers.takeover * ModuleCtx.Beyond_Takeovers
    takeover_limit = env.timers.takeover + HALimits.Server_Start

    # The traffic of the active pod to the API server is delayed beyond the takeover time ..
    delayed_at = delay_pod_traffic(active.pod_name, active.host_node, address, delay)

    try:

        # .. the standby takes over ..
        _ = standby.wait_for_role([ModuleCtx.Role_Active], takeover_limit)
        took_over_at = time.time()

    finally:
        remove_pod_delay(active.pod_name, active.host_node)

    logger.info('Standby %s active %.3fs after the delay began', standby.pod_name, took_over_at - delayed_at)

    # .. the record names it at a higher generation ..
    record = env.referee.read_record()
    assert record is not None, 'No referee record'
    assert record['active_node'] == standby.pod_name, record
    assert record['generation'] > generation, record

    # .. and the former active pod gives up the active role.
    _ = active.wait_for_role(ModuleCtx.Former_Active_Roles, ModuleCtx.Former_Active_Timeout)

# ################################################################################################################################
# ################################################################################################################################
