# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A failover of the database that both nodes share. The former primary is removed before a standby is promoted
# and the name of the endpoint moves to the promoted standby only once it accepts writes. A promotion of the
# synchronous standby loses nothing acknowledged and keeps the pair as it was. A promotion of a standby that lacks
# the last renewals of the lease keeps one server writing, as the active node continues under the version
# of the record and the server under its generation and owner. A promotion of a standby that lacks the last takeover
# stops every node whose persisted generation is higher than that of the record.

# stdlib
import logging
import time

# Zato
from ha_checks import check_publications_stored, check_scheduler, check_workload, watch_roles
from ha_takeover import ModuleCtx as TakeoverCtx
from ha_traffic import TimedPublisher
from postgresql_checks import check_active_server, wait_until_stopped
from postgresql_cluster import ModuleCtx as ClusterCtx
from postgresql_env import get_cluster
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

logger = logging.getLogger('zato.test.ha_postgresql.database_failover')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the failover and after it, in seconds
    Traffic_Seconds = 15

    # How long the roles of both nodes are watched once the promoted standby accepts writes, in seconds
    Watch_Seconds = 30

    # How long the pair may take to serve again after a failover, in seconds
    Recovery_Timeout = 300

    # How long the nodes may take to stop once the promoted standby lacks the last takeover, in seconds
    Stop_Timeout = 60

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # The synchronous standby and the one that the tests let fall behind
    Synchronous_Standby = ClusterCtx.Standby_Names[0]
    Lagging_Standby = ClusterCtx.Standby_Names[1]

# ################################################################################################################################
# ################################################################################################################################

def test_failover_to_synchronous_standby(ha_pair:'HAEnvironment') -> 'None':
    """ The primary fails under traffic and its synchronous standby is promoted. Nothing acknowledged is lost,
    the record keeps naming the active node at its generation, and the database accepts the writes of its server.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    record = cluster.read_record()
    assert record is not None
    generation_before = record['generation']

    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The primary fails and its synchronous standby is promoted ..
    fault_started = time.time()
    cluster.kill(cluster.primary_name)
    _ = cluster.promote(ModuleCtx.Synchronous_Standby)

    # .. after which the pair serves on it as it was.
    serving = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    assert serving is active, f'{serving.node_name} serves in place of {active.node_name}'

    time.sleep(ModuleCtx.Traffic_Seconds)
    workload.fault_windows.append((fault_started, time.time()))
    publisher.stop()

    record = cluster.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    check_workload(env, workload)
    check_publications_stored(env, active, publisher.get_msg_ids())

    _ = check_scheduler(env, active, ModuleCtx.Unrun_Claims_After_Isolation)
    check_active_server(env, active)

# ################################################################################################################################

def test_failover_to_standby_without_the_last_renewals(ha_pair:'HAEnvironment') -> 'None':
    """ A standby falls behind while the active node renews its lease, and it is promoted once the primary and the
    synchronous standby fail. The active node continues under the older version of the record, the nodes never
    serve at the same time, and the server of the active node writes what it acknowledges from then on.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    record = cluster.read_record()
    assert record is not None
    generation_before = record['generation']

    # A standby falls behind, while commits wait for the other one ..
    cluster.disconnect(ModuleCtx.Lagging_Standby)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # .. the primary and the synchronous standby fail, and the standby that fell behind is promoted ..
    cluster.kill(cluster.primary_name)
    cluster.kill(ModuleCtx.Synchronous_Standby)
    _ = cluster.promote(ModuleCtx.Lagging_Standby)

    promoted_at = time.time()

    # .. after which the active node serves on it alone ..
    serving = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    assert serving is active, f'{serving.node_name} serves in place of {active.node_name}'

    both_active = watch_roles(env, ModuleCtx.Watch_Seconds)
    assert not both_active, both_active

    publisher.stop()

    record = cluster.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    # .. and the database holds what its server acknowledged since the promotion.
    after_promotion = publisher.get_acknowledged_between(promoted_at, time.time())
    assert after_promotion, 'No publication acknowledged after the promotion'

    check_publications_stored(env, active, after_promotion)
    check_active_server(env, active)

# ################################################################################################################################

def test_failover_to_standby_without_the_last_takeover(ha_pair:'HAEnvironment') -> 'None':
    """ A standby falls behind, a takeover follows, and the standby is promoted once the primary and the synchronous
    standby fail. Its record holds the generation from before the takeover, below the one that both nodes persisted,
    so both nodes stop and no server writes.
    """
    env = ha_pair
    cluster = get_cluster(env)

    old_active = env.get_active()
    assert old_active is not None, 'No active node'

    new_active = env.get_other(old_active)

    # A standby falls behind ..
    cluster.disconnect(ModuleCtx.Lagging_Standby)

    # .. the active node fails, its standby takes over and the former active node joins again ..
    old_active.kill()

    _ = new_active.wait_for_role(TakeoverCtx.Active_Roles, TakeoverCtx.Takeover_Timeout)
    _ = new_active.wait_until_server_up(TakeoverCtx.Server_Timeout)

    old_active.resume()
    _ = old_active.wait_for_role(TakeoverCtx.Standby_In_Sync, TakeoverCtx.Rejoin_Timeout)

    record = cluster.read_record()
    assert record is not None
    taken_over_generation = record['generation']

    # .. and the standby without the takeover is promoted once the primary and the synchronous standby fail ..
    cluster.kill(cluster.primary_name)
    cluster.kill(ModuleCtx.Synchronous_Standby)
    _ = cluster.promote(ModuleCtx.Lagging_Standby)

    record = cluster.read_record()
    assert record is not None
    assert record['generation'] < taken_over_generation, record

    for node in env.node_list:
        persisted = node.read_generation_file()
        assert persisted > record['generation'], f'{node.node_name} persisted {persisted}, record {record}'

    # .. so both nodes stop.
    wait_until_stopped(env.node_list, ModuleCtx.Stop_Timeout)

# ################################################################################################################################
# ################################################################################################################################
