# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A failover of the database that both nodes share. The former primary is removed before a standby is promoted
# and the name of the endpoint moves to the promoted standby only once it accepts writes. The referee record is in
# the lease, so no failover of the database changes it. A promotion of the synchronous standby loses nothing
# acknowledged and keeps the pair as it was. A promotion of a standby that lacks the publications of the last seconds
# keeps one server writing, as the server continues under its generation and owner. A promotion of a standby that
# lacks the last takeover holds the generation and the owner of the former server, so the database accepts
# the writes of no server and no two nodes are active.

# stdlib
import logging
import time

# Zato
from ha_checks import check_publications_stored, check_scheduler, check_workload, watch_roles
from ha_takeover import ModuleCtx as TakeoverCtx
from ha_traffic import TimedPublisher
from postgresql_checks import check_active_server, read_active_server
from postgresql_cluster import ModuleCtx as ClusterCtx
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

    record = env.referee.read_record()
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

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == active.node_name, record
    assert record['generation'] == generation_before, record

    check_workload(env, workload)
    check_publications_stored(env, active, publisher.get_msg_ids())

    _ = check_scheduler(env, active, ModuleCtx.Unrun_Claims_After_Isolation)
    check_active_server(env, active)

# ################################################################################################################################

def test_failover_to_standby_without_the_last_publications(ha_pair:'HAEnvironment') -> 'None':
    """ A standby falls behind under traffic, and it is promoted once the primary and the synchronous standby fail.
    The record keeps naming the active node at its generation, the nodes never serve at the same time,
    and the server of the active node writes what it acknowledges from then on.
    """
    env = ha_pair
    cluster = get_cluster(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    record = env.referee.read_record()
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

    record = env.referee.read_record()
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
    standby fail. It names the server from before the takeover, whose node is the standby now, so the database
    accepts the writes of no server, the record keeps naming the node that took over, and no two nodes are active.
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

    record = env.referee.read_record()
    assert record is not None
    taken_over_generation = record['generation']

    # .. and the standby without the takeover is promoted once the primary and the synchronous standby fail ..
    cluster.kill(cluster.primary_name)
    cluster.kill(ModuleCtx.Synchronous_Standby)
    _ = cluster.promote(ModuleCtx.Lagging_Standby)

    # .. which names the server from before the takeover ..
    in_database = read_active_server(env)
    in_file = read_server_generation(new_active)
    assert in_database != in_file, f'Database names the server of {new_active.node_name} -> {in_database}'

    # .. while the record keeps naming the node that took over, and no two nodes are active.
    both_active = watch_roles(env, ModuleCtx.Watch_Seconds)
    assert not both_active, both_active

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == new_active.node_name, record
    assert record['generation'] == taken_over_generation, record

# ################################################################################################################################
# ################################################################################################################################
