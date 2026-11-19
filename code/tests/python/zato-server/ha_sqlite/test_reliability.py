# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The durability of what an active-standby pair acknowledges. Nodes lose their power with every write they did not sync
# discarded, the standby freezes while publications continue, the active node fails while it runs alone, and the link
# to the standby outlasts the barrier. No acknowledged publication is lost, no publication is acknowledged before
# it is on two disks or the referee names the active node alone, and a stale standby never becomes active.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies, check_publications_stored, has_message
from ha_env import ready_pair
from ha_lazyfs import LazyFSHook
from ha_tools import degrade_link, restore_link
from ha_traffic import TimedPublisher
from nodes import ModuleCtx as NodesCtx, Timers
from workload import Topic_Name
from zato.common.test.client import PublishClient, PullClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.reliability')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many publications the pair acknowledges before a fault
    Acknowledged_Before_Fault = 200

    # How long the publications may take to reach that number, in seconds
    Acknowledged_Timeout = 120

    # How long the traffic runs in a phase of a test, in seconds
    Traffic_Seconds = 5

    # How long a node may take to change its role, in seconds
    Role_Timeout = 60

    # How long the server of a node may take to start, in seconds
    Server_Timeout = 120

    # How long a pair may take to form again, in seconds
    Pair_Timeout = 300

    # How long the referee record is read while a test waits for it to name the active node alone, in seconds,
    # and how often
    Record_Timeout = 60
    Record_Poll_Interval = 0.1

    # How long a stale standby is watched after the active node failed, which is many takeover timers, in seconds
    Stale_Watch_Seconds = 30

    # How often the role of a stale standby is read while it is watched, in seconds
    Role_Poll_Interval = 0.2

    # The delay of the link to the standby, which outlasts the barrier of the active node, in milliseconds
    Barrier_Outlasting_Delay_Ms = 45000

    # How long the API server is unavailable before the link to the standby is delayed, in seconds
    Outage_Before_Delay_Seconds = 3

    # How many messages one pull asks for and how many empty pulls end a drain
    Pull_Max_Messages = 100
    Empty_Pulls_To_Stop = 3

    # How often the queue is pulled while it drains, in seconds, which outlasts the pull lease of the nodes
    Pull_Poll_Interval = 1.0

    # The roles of the pair
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_acknowledged(publisher:'TimedPublisher', count:'int') -> 'None':
    """ Waits until the publisher received the given number of acknowledgements.
    """
    deadline = time.monotonic() + ModuleCtx.Acknowledged_Timeout

    while len(publisher.get_msg_ids()) < count:
        assert time.monotonic() < deadline, f'Fewer than {count} publications acknowledged'
        time.sleep(ModuleCtx.Role_Poll_Interval)

# ################################################################################################################################

def _wait_for_active(node:'Node') -> 'None':
    """ Waits until a node is active and its server answers.
    """
    _ = node.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Role_Timeout)
    _ = node.wait_until_server_up(ModuleCtx.Server_Timeout)

# ################################################################################################################################

def _wait_for_solo_record(env:'HAEnvironment', active:'Node') -> 'float':
    """ Waits until the referee record names the given node active alone, and returns the last time
    at which the record still named its standby in sync, in seconds since the epoch.
    """
    deadline = time.monotonic() + ModuleCtx.Record_Timeout
    out = time.time()

    while True:
        read_started = time.time()
        record = env.referee.read_record()
        assert record is not None, 'No referee record'

        if not record['standby_in_sync']:
            assert record['active_node'] == active.node_name, record
            return out

        # The record named the standby in sync at least until the read began.
        out = read_started

        assert time.monotonic() < deadline, f'The referee record did not name {active.node_name} alone -> {record}'
        time.sleep(ModuleCtx.Record_Poll_Interval)

# ################################################################################################################################

def _drain_pulls(env:'HAEnvironment') -> 'strlist':
    """ Pulls and acknowledges the queue of the puller until it stays empty, and returns the msg_id of each message
    handed out, as many times as it was handed out.
    """
    client = PullClient(env.haproxy.base_url, env.puller_username, env.puller_password)

    out:'strlist' = []
    empty_pulls = 0

    while empty_pulls < ModuleCtx.Empty_Pulls_To_Stop:
        result = client.pull(max_messages=ModuleCtx.Pull_Max_Messages, needs_ack=True)

        if result['messages']:
            empty_pulls = 0
        else:
            empty_pulls += 1
            time.sleep(ModuleCtx.Pull_Poll_Interval)

        for message in result['messages']:
            meta = message['meta']
            out.append(meta['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_standby_power_loss(ha_session:'HASession', request:'any_') -> 'None':
    """ The standby loses its power with its unsynced writes discarded and joins again, the active node then fails,
    and the standby takes over with every acknowledged publication.
    """
    lazyfs = LazyFSHook()

    with ready_pair(ha_session, request.node.name, Timers(), [lazyfs]) as env:

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
        publisher.start()

        _wait_for_acknowledged(publisher, ModuleCtx.Acknowledged_Before_Fault)

        # The standby loses its power ..
        standby.kill()
        lazyfs.discard_unsynced(standby)

        # .. and joins again from a copy of the active node ..
        standby.resume()
        _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Pair_Timeout)

        time.sleep(ModuleCtx.Traffic_Seconds)

        # .. after which the active node fails and the standby takes over.
        active.kill()
        _wait_for_active(standby)
        env.point_database_at(standby)

        time.sleep(ModuleCtx.Traffic_Seconds)
        publisher.stop()

        check_publications_stored(env, standby, publisher.get_msg_ids())

        active.resume()
        _ = active.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Pair_Timeout)

        check_copies(env, standby)

# ################################################################################################################################

def test_power_loss_of_both_nodes(ha_session:'HASession', request:'any_') -> 'None':
    """ Both nodes lose their power at once with their unsynced writes discarded, and the node that becomes active
    once both start again holds every acknowledged publication.
    """
    lazyfs = LazyFSHook()

    with ready_pair(ha_session, request.node.name, Timers(), [lazyfs]) as env:

        publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
        publisher.start()

        _wait_for_acknowledged(publisher, ModuleCtx.Acknowledged_Before_Fault)

        # Both nodes lose their power ..
        for node in env.node_list:
            node.kill()

        for node in env.node_list:
            lazyfs.discard_unsynced(node)

        publisher.stop()

        # .. both start again ..
        for node in env.node_list:
            node.resume()

        # .. and the active node holds everything that was acknowledged.
        active = env.wait_for_pair(ModuleCtx.Pair_Timeout)

        check_publications_stored(env, active, publisher.get_msg_ids())
        check_copies(env, active)

# ################################################################################################################################

def test_entry_into_solo_running(ha_pair:'HAEnvironment') -> 'None':
    """ No publication sent after the standby froze is acknowledged before the referee record names the active node
    alone, and every acknowledged publication is stored.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The standby freezes while the publications continue ..
    standby.pause()
    frozen = time.time()

    # .. and nothing sent after that is acknowledged while the record still names the standby in sync.
    last_in_sync = _wait_for_solo_record(env, active)

    acknowledged = publisher.get_acknowledged_between(frozen, last_in_sync)
    assert not acknowledged, f'Acknowledged without the standby while the record named it in sync -> {acknowledged}'

    # The active node continues alone ..
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Role_Timeout)
    solo_started = time.time()

    time.sleep(ModuleCtx.Traffic_Seconds)

    solo_acknowledged = publisher.get_acknowledged_between(solo_started, time.time())
    assert solo_acknowledged, 'No publication acknowledged in solo running'

    # .. and admits the standby again once it resumes.
    standby.unpause()
    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Pair_Timeout)

    publisher.stop()

    check_publications_stored(env, active, publisher.get_msg_ids())
    check_copies(env, active)

# ################################################################################################################################

def test_solo_acknowledgements_on_disk(ha_session:'HASession', request:'any_') -> 'None':
    """ The active node runs alone and loses its power with its unsynced writes discarded, and once it starts again,
    it holds every publication it acknowledged while it ran alone.
    """
    lazyfs = LazyFSHook()

    with ready_pair(ha_session, request.node.name, Timers(), [lazyfs]) as env:

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
        publisher.start()

        # The standby fails and the active node continues alone ..
        standby.kill()
        _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Role_Timeout)
        solo_started = time.time()

        time.sleep(ModuleCtx.Traffic_Seconds)

        # .. until it loses its power ..
        active.kill()
        lazyfs.discard_unsynced(active)
        power_lost = time.time()

        publisher.stop()

        solo_acknowledged = publisher.get_acknowledged_between(solo_started, power_lost)
        assert solo_acknowledged, 'No publication acknowledged in solo running'

        # .. and once it starts again, it holds every publication acknowledged while it ran alone.
        active.resume()
        _wait_for_active(active)
        env.point_database_at(active)

        check_publications_stored(env, active, solo_acknowledged)

        standby.resume()
        _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Pair_Timeout)

        check_copies(env, active)

# ################################################################################################################################

def test_no_promotion_of_stale_standby(ha_pair:'HAEnvironment') -> 'None':
    """ The active node runs alone and fails, and its former standby, which starts while the record names the active
    node alone, never becomes active and acknowledges nothing until the former active node returns.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    # The standby fails and the active node continues alone ..
    standby.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Role_Timeout)

    # .. until it fails too ..
    active.kill()

    # .. after which the former standby starts with a copy that lacks what the active node acknowledged alone ..
    standby.resume()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    watch_started = time.time()
    deadline = time.monotonic() + ModuleCtx.Stale_Watch_Seconds

    # .. and it never becomes active ..
    while time.monotonic() < deadline:
        assert not standby.is_active(), f'{standby.node_name} became active with a stale copy'
        time.sleep(ModuleCtx.Role_Poll_Interval)

    # .. nor acknowledges anything.
    acknowledged = publisher.get_acknowledged_between(watch_started, time.time())
    assert not acknowledged, f'Acknowledged by a stale standby -> {acknowledged}'

    # Once the former active node returns, it is active again and the standby joins it.
    active.resume()
    returned = env.wait_for_pair(ModuleCtx.Pair_Timeout)
    assert returned.node_name == active.node_name, f'{returned.node_name} became active instead of {active.node_name}'

    publisher.stop()

    check_publications_stored(env, active, publisher.get_msg_ids())
    check_copies(env, active)

# ################################################################################################################################

def test_barrier_timeout(ha_pair:'HAEnvironment') -> 'None':
    """ A publication whose barrier outlasts its timeout raises an error to its caller, and a retry with the same
    msg_id results in exactly one stored and delivered message.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    client = PublishClient(env.haproxy.base_url, env.publisher_username, env.publisher_password)

    msg_id = f'zpsm.durability.barrier.{time.time_ns()}'
    data = {'barrier_timeout': msg_id}

    # The API server is unavailable, so the active node cannot mark its standby out ..
    env.referee.stop()
    time.sleep(ModuleCtx.Outage_Before_Delay_Seconds)

    # .. the link to the standby is slower than the barrier waits for ..
    delay = f'delay {ModuleCtx.Barrier_Outlasting_Delay_Ms}ms'
    degrade_link(active, [standby.ip], delay)
    degrade_link(standby, [active.ip], delay)

    # .. so the publication raises an error to its caller ..
    try:
        _ = client.publish(Topic_Name, data, msg_id=msg_id)
    except Exception as e:
        logger.info('Publication refused as expected -> %s', e)
    else:
        raise AssertionError(f'Publication {msg_id} acknowledged although its barrier timed out')

    # .. the link and the API server recover ..
    restore_link(active)
    restore_link(standby)
    env.referee.resume()

    active = env.wait_for_pair(ModuleCtx.Pair_Timeout)

    # .. the caller retries with the same msg_id ..
    result = client.publish(Topic_Name, data, msg_id=msg_id)
    assert result['msg_id'] == msg_id, result

    # .. and there is exactly one message, which is delivered once.
    assert has_message(active, msg_id), f'{msg_id} not stored'

    pulled = _drain_pulls(env)
    count = pulled.count(msg_id)
    assert count == 1, f'{msg_id} delivered {count} times'

    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
