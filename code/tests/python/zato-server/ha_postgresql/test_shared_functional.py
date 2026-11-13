# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The pair on PostgreSQL as it forms and serves - one node active alone with the other its standby, the role endpoint
# answering on the active node only, HAProxy routing to the active node through a restart and through takeovers,
# and the scheduler keeping its run state in the database that both nodes share.

# stdlib
import logging
import time
from http.client import OK, SERVICE_UNAVAILABLE
from urllib.error import HTTPError
from urllib.request import urlopen

# Zato
from checks import get_starts, read_run_log
from ha_checks import check_no_runs_after, check_publications_stored, check_scheduler
from ha_traffic import TimedPublisher
from postgresql_checks import check_active_server
from postgresql_cluster import ModuleCtx as ClusterCtx
from workload import read_rows
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

logger = logging.getLogger('zato.test.ha_postgresql.functional')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The roles of a pair that formed on the database both nodes share
    Role_Active  = 'ActiveSolo'
    Role_Standby = 'StandbyInSync'

    # How long a request to the role endpoint or through HAProxy may take, in seconds
    Request_Timeout = 5

    # How long the scheduler runs before its run state is compared with the run logs, in seconds
    Scheduler_Seconds = 30

    # How long the traffic runs around each event, in seconds
    Traffic_Seconds = 10

    # How many takeovers the test of HAProxy measures
    Takeover_Count = 2

    # How long clients may take to reach the active node after HAProxy restarts and after a takeover, in seconds
    Restart_Recovery_Limit = 10
    Takeover_Recovery_Limit = 180

    # How often the test checks whether clients reach the active node, in seconds
    Poll_Interval = 0.2

    # How long the former active node may take to join again as the standby, in seconds
    Rejoin_Timeout = 300

# ################################################################################################################################
# ################################################################################################################################

def _get_pair(env:'HAEnvironment') -> 'tuple[Node, Node]':
    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    out = (active, standby)
    return out

# ################################################################################################################################

def _read_role_status(node:'Node') -> 'int':
    """ Returns the status code with which the role endpoint of a node answers.
    """
    try:
        with urlopen(node.role_url, timeout=ModuleCtx.Request_Timeout) as response:
            out = response.status
    except HTTPError as e:
        out = e.code

    return out

# ################################################################################################################################

def _wait_for_acknowledgment(publisher:'TimedPublisher', start:'float', limit:'float') -> 'float':
    """ Waits until a publication sent after the given time is acknowledged, and returns how long it took, in seconds.
    """
    while True:
        acknowledged = publisher.get_acknowledged_between(start, time.time())

        if acknowledged:
            out = time.time() - start
            return out

        elapsed = time.time() - start
        assert elapsed < limit, f'No publication acknowledged within {limit}s'

        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def test_bootstrap(ha_pair:'HAEnvironment') -> 'None':
    """ One node is active alone with the other its standby, both hold the generation of the record, which names
    the active node, no node publishes an address, the role endpoint answers on the active node only, the Zato server
    runs on the active node only, HAProxy reaches it and the database accepts the writes of that server.
    """
    env = ha_pair
    active, standby = _get_pair(env)

    active_report = active.read_role()
    standby_report = standby.read_role()

    assert active_report is not None
    assert standby_report is not None

    assert active_report['role'] == ModuleCtx.Role_Active, active_report
    assert standby_report['role'] == ModuleCtx.Role_Standby, standby_report

    record = env.referee.read_record()
    assert record is not None

    assert record['active_node'] == active.node_name, record
    assert active_report['generation'] == record['generation'], (active_report, record)
    assert standby_report['generation'] == record['generation'], (standby_report, record)

    # The record of the pair is the only row of the referee, as the nodes publish no address ..
    keys:'list[str]' = []

    for row in read_rows(cast_('any_', env), 'select key from zato_ha_referee'):
        keys.append(row[0])

    assert keys == [ClusterCtx.Record_Key], keys

    # .. the role endpoint answers on the active node only ..
    assert _read_role_status(active) == OK
    assert _read_role_status(standby) == SERVICE_UNAVAILABLE

    # .. the server runs only where the node is active ..
    assert active.is_server_up()
    assert not standby.is_server_up()

    # .. HAProxy reaches it ..
    with urlopen(f'{env.haproxy.base_url}/zato/ping', timeout=ModuleCtx.Request_Timeout) as response:
        assert response.status == OK

    # .. and the database accepts the writes of its server.
    check_active_server(env, active)

# ################################################################################################################################

def test_scheduler(ha_pair:'HAEnvironment') -> 'None':
    """ The scheduler of the active node runs its jobs with their run state in the shared database, and the standby
    runs none of them.
    """
    env = ha_pair
    active, standby = _get_pair(env)

    time.sleep(ModuleCtx.Scheduler_Seconds)

    entries = read_run_log(cast_('any_', env))
    assert get_starts(entries), 'No scheduler run began'

    _ = check_scheduler(env, active)
    check_no_runs_after(env, standby, 0.0)

# ################################################################################################################################

def test_haproxy(ha_pair:'HAEnvironment') -> 'None':
    """ Clients reach the active node again shortly after HAProxy restarts, and after each takeover within the time
    of the takeover and of the start of the new server, and the database holds every acknowledged publication.
    """
    env = ha_pair

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # HAProxy restarts under traffic ..
    restarted_at = time.time()
    env.haproxy.restart()

    restart_recovery = _wait_for_acknowledgment(publisher, restarted_at, ModuleCtx.Restart_Recovery_Limit)
    logger.info('Clients reached the active node %.2fs after HAProxy restarted', restart_recovery)

    # .. and the active node is killed, once per takeover.
    for _ in range(ModuleCtx.Takeover_Count):
        active, standby = _get_pair(env)

        killed_at = time.time()
        active.kill()

        takeover_recovery = _wait_for_acknowledgment(publisher, killed_at, ModuleCtx.Takeover_Recovery_Limit)
        logger.info('Clients reached %s %.2fs after %s was killed', standby.node_name, takeover_recovery,
            active.node_name)

        active.resume()
        _ = active.wait_for_role([ModuleCtx.Role_Standby], ModuleCtx.Rejoin_Timeout)

    publisher.stop()

    active, _ = _get_pair(env)

    check_publications_stored(env, active, publisher.get_msg_ids())
    check_active_server(env, active)

# ################################################################################################################################
# ################################################################################################################################
