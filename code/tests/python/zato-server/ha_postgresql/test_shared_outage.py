# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The database unavailable to both nodes, the API server unavailable to both nodes, and the leases without the record
# of the pair. During an outage of the database the active node does not renew its lease, and the standby does not
# take over while its own probe of the database fails, so no takeover takes place during the outage, and the pair serves
# again once the database returns. During an outage of the API server the active node keeps serving, since the database
# refuses the transactions of a replaced server, and the standby restarts its measure at every read that fails,
# so no takeover takes place. Leases without the record of the pair stop both nodes, and neither of them creates
# a new record.

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

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.outage')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the database or the API server is unavailable, in seconds
    Outage_Seconds = [10, 120]

    # How long the traffic runs before the outage and after it, in seconds
    Traffic_Seconds = 10

    # How long the pair may take to serve again once the database returns, in seconds
    Return_Timeout = 120

    # How long both nodes may take to stop once the leases lost the record, in seconds
    Stop_Timeout = 60

    # The role of the standby
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', ModuleCtx.Outage_Seconds)
def test_database_outage(ha_pair:'HAEnvironment', outage_seconds:'int') -> 'None':
    """ No takeover takes place while the database is unavailable to both nodes, the pair serves again once it returns,
    and the database names the server of the active node.
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

    # The database becomes unavailable to both nodes, and the lease of the active node lapses ..
    cluster.stop()
    time.sleep(outage_seconds)

    # .. while no node takes over ..
    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    # .. until the database returns, after which the pair serves again.
    cluster.resume()
    serving = env.wait_for_pair(ModuleCtx.Return_Timeout)

    resumed_at = time.time()
    time.sleep(ModuleCtx.Traffic_Seconds)
    publisher.stop()

    after_outage = publisher.get_acknowledged_between(resumed_at, time.time())
    assert after_outage, 'No publication acknowledged once the database returned'

    check_active_server(env, serving)

# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', ModuleCtx.Outage_Seconds)
def test_api_server_outage(ha_pair:'HAEnvironment', outage_seconds:'int') -> 'None':
    """ The active node keeps acknowledging publications while the API server is unavailable to both nodes,
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

    # The API server becomes unavailable to both nodes ..
    outage_started = time.time()
    env.referee.stop()

    time.sleep(outage_seconds)

    outage_ended = time.time()
    env.referee.resume()

    time.sleep(ModuleCtx.Traffic_Seconds)
    publisher.stop()

    # .. the active node acknowledged publications throughout ..
    during_outage = publisher.get_acknowledged_between(outage_started, outage_ended)
    assert during_outage, 'No publication acknowledged during the outage'

    # .. and the standby never took over.
    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    report = standby.read_role()
    assert report is not None
    assert report['role'] == ModuleCtx.Standby_In_Sync, report

    _ = check_scheduler(env, active)
    check_active_server(env, active)

# ################################################################################################################################

def test_record_lost(ha_pair:'HAEnvironment') -> 'None':
    """ Leases without the record of the pair, while both nodes have seen a generation, stop both nodes
    with an error, and neither of them creates a new record.
    """
    env = ha_pair

    env.referee.recreate_without_data()
    wait_until_stopped(env.node_list, ModuleCtx.Stop_Timeout)

    record = env.referee.read_record()
    assert record is None, f'A new record was created -> {record}'

# ################################################################################################################################
# ################################################################################################################################
