# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The referee record in a lease, the API server unavailable and the leases without their data. Every change of the record
# is a compare-and-set, so a write under an earlier version is refused. With the standby in sync, the active node
# continues through an outage of the API server. A standby lost during the outage stops every acknowledgment until
# the API server returns, and clients receive errors, never success. Leases deleted while the pair runs stop both nodes.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler
from ha_traffic import TimedPublisher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from topology import Lease

    Lease = Lease

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.lease')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the API server is unavailable, in seconds
    Outage_Seconds = [10, 120]

    # How long the traffic runs before the outage and after it, in seconds
    Traffic_Seconds = 10

    # How long after the standby fails the requests in flight may still return, in seconds
    In_Flight_Grace = 1.0

    # How long the active node may take to mark the standby out once the API server returns, in seconds
    Mark_Out_Timeout = 60

    # How long the standby may take to join again, in seconds
    Rejoin_Timeout = 300

    # How long both nodes may take to stop once the referee lost its data, in seconds
    Stop_Timeout = 60

    # How often the containers are checked while a test waits for them to stop, in seconds
    Poll_Interval = 0.5

    # How many claims of each scheduler job the stop of an isolated server may leave without a run
    Unrun_Claims_After_Isolation = 1

    # What the log of a node contains once the referee lost its data
    Data_Loss_Text = 'the referee lost data'

    # The status of a JSON Patch whose test of the version failed
    Stale_Version_Status = 422

    # The roles of the pair
    Active_Replicated = ['ActiveReplicated']
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def test_the_record_follows_compare_and_set(ha_pair:'HAEnvironment') -> 'None':
    """ A mark-out writes the record under its version, which raises the version, and a write under the version
    from before the mark-out is refused and leaves the record as the mark-out wrote it.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    # The record names both nodes ..
    before = env.referee.read_record()
    assert before is not None, 'No referee record'
    assert before['active_node'] == active.node_name, before
    assert before['standby_node'] == standby.node_name, before
    assert before['standby_in_sync'], before

    # .. the active node marks out the standby that failed, under the version it read ..
    standby.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    after = env.referee.read_record()
    assert after is not None, 'No referee record after the mark-out'
    assert after['generation'] == before['generation'] + 1, (before, after)
    assert after['active_node'] == active.node_name, after
    assert after['version'] != before['version'], (before, after)

    # .. and a write under the version from before the mark-out is refused.
    status = env.referee.write_record(before, before['version'])
    assert status == ModuleCtx.Stale_Version_Status, status

    current = env.referee.read_record()
    assert current == after, (after, current)

    standby.resume()
    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', ModuleCtx.Outage_Seconds)
def test_outage_with_standby_in_sync(ha_pair:'HAEnvironment', outage_seconds:'int') -> 'None':
    """ The active node keeps acknowledging publications while the API server is unavailable and its standby in sync.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    outage_started = time.time()
    env.referee.stop()

    time.sleep(outage_seconds)

    outage_ended = time.time()
    env.referee.resume()

    time.sleep(ModuleCtx.Traffic_Seconds)
    publisher.stop()

    during_outage = publisher.get_acknowledged_between(outage_started, outage_ended)
    assert during_outage, 'No publication acknowledged during the outage'

    _ = active.wait_for_role(ModuleCtx.Active_Replicated, ModuleCtx.Mark_Out_Timeout)
    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################

def test_standby_lost_during_outage(ha_pair:'HAEnvironment') -> 'None':
    """ With the API server unavailable, the active node cannot mark out a standby that failed, so it acknowledges
    nothing and clients receive errors until the API server returns, after which it continues alone and admits
    the standby again.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # The API server becomes unavailable and the standby fails during the outage ..
    env.referee.stop()
    time.sleep(ModuleCtx.Traffic_Seconds)

    standby_failed = time.time()
    standby.kill()

    time.sleep(ModuleCtx.Outage_Seconds[-1])

    # .. so nothing is acknowledged until the API server returns ..
    outage_ended = time.time()

    acknowledged = publisher.get_acknowledged_between(standby_failed + ModuleCtx.In_Flight_Grace, outage_ended)
    assert not acknowledged, f'Acknowledged without the standby and the referee -> {acknowledged}'

    errors = publisher.count_errors_after(standby_failed)
    assert errors > 0, 'No client received an error during the outage'

    # .. after which the active node marks the standby out and continues alone ..
    env.referee.resume()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)
    _ = active.wait_until_server_up(ModuleCtx.Mark_Out_Timeout)

    resumed_at = time.time()
    time.sleep(ModuleCtx.Traffic_Seconds)

    after_outage = publisher.get_acknowledged_between(resumed_at, time.time())
    assert after_outage, 'No publication acknowledged once the API server returned'

    # .. and admits the standby again.
    standby.resume()
    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

    publisher.stop()

    # A claim that the barrier held when the standby failed is in the copy of the active node,
    # and the server was stopped before it ran the job.
    _ = check_scheduler(env, active, ModuleCtx.Unrun_Claims_After_Isolation)
    check_copies(env, active)

# ################################################################################################################################

def test_referee_data_loss(ha_pair:'HAEnvironment') -> 'None':
    """ Leases deleted while the pair runs hold no record while both nodes have seen a generation,
    so both nodes stop with an error and neither bootstraps a new generation.
    """
    env = ha_pair
    env.referee.recreate_without_data()

    deadline = time.monotonic() + ModuleCtx.Stop_Timeout

    while True:
        running:'list[str]' = []

        for node in env.node_list:
            if node.is_running():
                running.append(node.node_name)

        if not running:
            break

        assert time.monotonic() < deadline, f'Still running after the referee lost its data -> {running}'
        time.sleep(ModuleCtx.Poll_Interval)

    for node in env.node_list:
        logs = node.read_logs()
        assert ModuleCtx.Data_Loss_Text in logs, f'{node.node_name} stopped without the error of a referee that lost data'

    record = env.referee.read_record()
    assert record is None, f'A new generation was bootstrapped -> {record}'

# ################################################################################################################################
# ################################################################################################################################
