# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The durability of a pair on PostgreSQL. A cluster whose standbys stream asynchronously is refused when the pair
# starts, and once the synchronous setting is removed while the pair serves, the active node stops serving within
# one probe of the database. A loss of power to the primary and to its synchronous standby at once loses
# no acknowledged publication.

# stdlib
import logging
import time

# Zato
from ha_checks import check_publications_stored
from ha_env import clear_receivers, remove_environment
from ha_traffic import TimedPublisher
from nodes import Timers
from postgresql_cluster import ModuleCtx as ClusterCtx
from postgresql_env import build_environment, get_cluster, ready_pair_on_lazyfs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.durability')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What the log of a node contains once the database is found not durable
    Reason_Text = 'synchronous_standby_names'

    # How long a pair on an asynchronous cluster is watched, in seconds
    Refusal_Watch_Seconds = 30

    # How long the traffic runs before a fault, in seconds
    Traffic_Seconds = 5

    # How long one probe of the database may take, as the node bounds it, in seconds
    Probe_Timeout = 2.0

    # How often the role of a node is read while a test waits for it, in seconds
    Poll_Interval = 0.1

    # How long after a node stops serving the requests in flight may still return, in seconds
    In_Flight_Grace = 1.0

    # How long the pair may take to serve again, in seconds
    Return_Timeout = 180

    # The instances that lose power together - the primary and the standby that each commit waits for
    Power_Loss_Names = [ClusterCtx.First_Primary, ClusterCtx.Standby_Names[0]]

# ################################################################################################################################
# ################################################################################################################################

def _wait_until_isolated(node:'Node', timeout:'float') -> 'float':
    """ Waits until a node reports that it is isolated and returns the time, in seconds since the epoch,
    at which it was first seen so.
    """
    deadline = time.monotonic() + timeout

    while True:
        report = node.read_role()

        if report is not None:
            if report['isolated']:
                out = time.time()
                return out

        assert time.monotonic() < deadline, f'{node.node_name} not isolated after {timeout}s, report -> {report}'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _check_reason_logged(nodes:'list[Node]') -> 'None':
    """ Checks that the log of at least one of the nodes names the setting that makes the database not durable.
    """
    logged_by:'strlist' = []

    for node in nodes:
        if ModuleCtx.Reason_Text in node.read_logs():
            logged_by.append(node.node_name)

    assert logged_by, f'No node logged `{ModuleCtx.Reason_Text}`'

# ################################################################################################################################
# ################################################################################################################################

def test_asynchronous_cluster_refused(ha_session:'HASession', request:'any_') -> 'None':
    """ A pair whose cluster has only asynchronous standbys never serves and acknowledges no publication,
    and the nodes report synchronous_standby_names as the reason.
    """
    clear_receivers(ha_session)
    env = build_environment(ha_session, request.node.name, Timers(), [], False, [])

    try:
        publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
        publisher.start()

        time.sleep(ModuleCtx.Refusal_Watch_Seconds)
        publisher.stop()

        acknowledged = publisher.get_msg_ids()
        assert not acknowledged, f'Publications acknowledged on an asynchronous cluster -> {acknowledged}'

        active = env.get_active()
        assert active is None, f'{active.node_name} serves on an asynchronous cluster'

        _check_reason_logged(env.node_list)

    finally:
        remove_environment(env)

# ################################################################################################################################

def test_asynchronous_standby_at_runtime(ha_pair:'HAEnvironment') -> 'None':
    """ Once the primary stops waiting for its streaming standbys while the pair serves, the active node stops serving
    within one probe of the database, no node acknowledges a publication from then on, the standby does not take over
    and the active node reports synchronous_standby_names as the reason. The pair serves again once the setting returns.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The primary keeps both standbys streaming and waits for none of them ..
    changed_at = time.time()
    cluster.set_synchronous_standby_names('')

    # .. the active node stops serving within one probe ..
    detection_bound = env.timers.heartbeat + ModuleCtx.Probe_Timeout + ModuleCtx.Poll_Interval
    isolated_at = _wait_until_isolated(active, detection_bound)
    logger.info('%s isolated %.3fs after the change', active.node_name, isolated_at - changed_at)

    # .. and no node acknowledges a publication while the database is not durable, including after the takeover time.
    time.sleep(env.timers.takeover + ModuleCtx.Traffic_Seconds)
    watch_ended = time.time()

    acknowledged = publisher.get_acknowledged_between(isolated_at + ModuleCtx.In_Flight_Grace, watch_ended)
    assert not acknowledged, f'Publications acknowledged while the database was not durable -> {acknowledged}'

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    _check_reason_logged([active])

    # Each commit waits for a standby again, after which the pair serves again.
    cluster.set_synchronous_standby_names(ClusterCtx.Synchronous_Standby_Names)
    _ = env.wait_for_pair(ModuleCtx.Return_Timeout)

    resumed_at = time.time()
    time.sleep(ModuleCtx.Traffic_Seconds)
    publisher.stop()

    after_return = publisher.get_acknowledged_between(resumed_at, time.time())
    assert after_return, 'No publication acknowledged once the database was durable again'

# ################################################################################################################################

def test_power_loss_of_primary_and_standby(ha_session:'HASession', request:'any_') -> 'None':
    """ The primary and its synchronous standby lose power at once, with every write that was not synced discarded
    on both, and once both return, every publication acknowledged before the loss is in the database.
    """
    timers = Timers()

    with ready_pair_on_lazyfs(ha_session, request.node.name, timers, ModuleCtx.Power_Loss_Names) as env:
        cluster = get_cluster(env)

        publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
        publisher.start()

        time.sleep(ModuleCtx.Traffic_Seconds)

        # Both instances lose power while publications are in flight ..
        cluster.cut_power(ModuleCtx.Power_Loss_Names)
        publisher.stop()

        acknowledged = publisher.get_msg_ids()
        assert acknowledged, 'No publication acknowledged before the loss of power'

        # .. both return with what their disks hold ..
        for name in ModuleCtx.Power_Loss_Names:
            cluster.restart(name)

        active = env.wait_for_pair(ModuleCtx.Return_Timeout)

        # .. and every acknowledged publication is in the database.
        check_publications_stored(env, active, acknowledged)

# ################################################################################################################################
# ################################################################################################################################
