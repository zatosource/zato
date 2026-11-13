# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The database unavailable to both nodes or without the record of the pair. During an outage the active node cannot
# renew its lease and is isolated, which stops its server, while the standby restarts its measure at every read that
# fails, so no takeover takes place and the active node serves again once the database returns. A database without
# the record of the pair stops both nodes, and neither of them creates a new record.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_scheduler
from ha_traffic import TimedPublisher
from postgresql_checks import check_active_server, wait_until_stopped
from postgresql_env import get_cluster

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.outage')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the database is unavailable, in seconds
    Outage_Seconds = [10, 120]

    # How long the traffic runs before the outage and after it, in seconds
    Traffic_Seconds = 10

    # How long the active node may take to be isolated and to stop its server once the outage begins,
    # beyond its mark-out time, in seconds
    Isolation_Margin = 10

    # How long the active node may take to serve again once the database returns, in seconds
    Return_Timeout = 120

    # How long both nodes may take to stop once the database lost the record, in seconds
    Stop_Timeout = 60

    # How often the role of the active node is read while the test waits for it, in seconds
    Poll_Interval = 0.2

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # The role of the standby
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_isolation(node:'Node', is_isolated:'bool', timeout:'float') -> 'None':
    """ Waits until a node reports the given isolation, with its server stopped while it is isolated
    and answering otherwise.
    """
    deadline = time.monotonic() + timeout

    while True:
        report = node.read_role()

        if report is not None:
            if report['isolated'] == is_isolated:
                if node.is_server_up() != is_isolated:
                    return

        assert time.monotonic() < deadline, f'{node.node_name} not isolated={is_isolated} after {timeout}s -> {report}'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', ModuleCtx.Outage_Seconds)
def test_database_outage(ha_pair:'HAEnvironment', outage_seconds:'int') -> 'None':
    """ The active node is isolated during an outage of the database and serves again once it returns,
    the standby does not take over, and the record keeps naming the active node at its generation.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The database becomes unavailable to both nodes, and the active node is isolated ..
    outage_started = time.monotonic()
    env.referee.stop()

    isolation_timeout = env.timers.mark_out + ModuleCtx.Isolation_Margin
    _wait_for_isolation(active, True, isolation_timeout)

    elapsed = time.monotonic() - outage_started
    time.sleep(max(outage_seconds - elapsed, 0))

    # .. until the database returns, after which it serves again ..
    env.referee.resume()
    _wait_for_isolation(active, False, ModuleCtx.Return_Timeout)

    resumed_at = time.time()
    time.sleep(ModuleCtx.Traffic_Seconds)
    publisher.stop()

    after_outage = publisher.get_acknowledged_between(resumed_at, time.time())
    assert after_outage, 'No publication acknowledged once the database returned'

    # .. while the standby never took over.
    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    report = standby.read_role()
    assert report is not None
    assert report['role'] == ModuleCtx.Standby_In_Sync, report

    _ = check_scheduler(env, active, ModuleCtx.Unrun_Claims_After_Isolation)
    check_active_server(env, active)

# ################################################################################################################################

def test_record_lost(ha_pair:'HAEnvironment') -> 'None':
    """ A database without the record of the pair, while both nodes have seen a generation, stops both nodes
    with an error, and neither of them creates a new record.
    """
    env = ha_pair
    cluster = get_cluster(env)

    cluster.delete_record()
    wait_until_stopped(env.node_list, ModuleCtx.Stop_Timeout)

    record = cluster.read_record()
    assert record is None, f'A new record was created -> {record}'

# ################################################################################################################################
# ################################################################################################################################
