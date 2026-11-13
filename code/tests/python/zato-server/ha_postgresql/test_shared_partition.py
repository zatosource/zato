# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two nodes partitioned from each other while both reach the database, and the active node partitioned from
# the database while it reaches the API server. The nodes of the shared storage mode exchange nothing directly,
# so the first partition leaves the active node renewing its lease and no takeover takes place however long
# the partition lasts. In the second, the active node lets its lease lapse, the standby takes over, the database
# refuses every later transaction of the former server, and the former active node rejoins as the standby.

# stdlib
import logging
import time

# Zato
from ha_checks import check_publications_stored, check_scheduler, check_workload, watch_roles
from ha_faults import heal, partition
from ha_takeover import ModuleCtx as TakeoverCtx
from ha_traffic import TimedPublisher
from postgresql_checks import check_active_server, read_active_server
from postgresql_env import get_cluster, read_server_generation
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.partition')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the partition, in seconds
    Traffic_Seconds = 10

    # How long the partition lasts, many times the takeover time, in seconds
    Partition_Seconds = 90

    # How long the pair may take to form again once the former active node reaches the database, in seconds
    Recovery_Timeout = 300

    # The role of the standby
    Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

def test_partition_between_nodes(ha_pair:'HAEnvironment') -> 'None':
    """ While the nodes do not reach each other and both reach the database, the record keeps naming the active node
    at its generation, the nodes never serve at the same time, and nothing acknowledged is lost.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The nodes lose each other ..
    partition(active, [standby.ip])
    partition(standby, [active.ip])

    both_active = watch_roles(env, ModuleCtx.Partition_Seconds)
    assert not both_active, both_active

    # .. and nothing changes, since neither of them depends on the other.
    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    assert active.is_active(), active.read_role()

    report = standby.read_role()
    assert report is not None
    assert report['role'] == ModuleCtx.Standby_In_Sync, report

    heal(active)
    heal(standby)

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_active_server(env, active)

# ################################################################################################################################

def test_active_node_without_the_database(ha_pair:'HAEnvironment') -> 'None':
    """ The active node loses the database while it reaches the API server. Its lease lapses and the standby takes over
    at a higher generation, the database names the server of the new active node only, the former active node rejoins
    as the standby once it reaches the database again, and every acknowledged publication is stored.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The active node loses the database and stops renewing its lease ..
    partition(active, [cluster.ip])

    # .. the standby takes over at a higher generation ..
    _ = standby.wait_for_role(TakeoverCtx.Active_Roles, TakeoverCtx.Takeover_Timeout)
    _ = standby.wait_until_server_up(TakeoverCtx.Server_Timeout)

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == standby.node_name, record
    assert record['generation'] > generation_before, record

    # .. the database names its server only, which refuses the transactions of the former server ..
    check_active_server(env, standby)
    assert read_server_generation(active) != read_active_server(env)

    # .. the former active node reaches the database again and rejoins as the standby ..
    heal(active)

    serving = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    assert serving is standby, f'{serving.node_name} serves in place of {standby.node_name}'

    both_active = watch_roles(env, ModuleCtx.Traffic_Seconds)
    assert not both_active, both_active

    publisher.stop()

    # .. and the database holds every publication that a server acknowledged.
    check_publications_stored(env, standby, publisher.get_msg_ids())
    check_active_server(env, standby)

# ################################################################################################################################
# ################################################################################################################################
