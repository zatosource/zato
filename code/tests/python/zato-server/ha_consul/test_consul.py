# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The referee unavailable or without its data. With the standby in sync, the active node continues through
# an outage of Consul. A standby lost during the outage stops every acknowledgment until Consul returns,
# and clients receive errors, never success. A Consul recreated without its data stops both nodes.

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

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.consul')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long Consul is unavailable, in seconds
    Outage_Seconds = [10, 120]

    # How long the traffic runs before the outage and after it, in seconds
    Traffic_Seconds = 10

    # How long after the standby fails the requests in flight may still return, in seconds
    In_Flight_Grace = 1.0

    # How long the active node may take to mark the standby out once Consul returns, in seconds
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

    # The roles of the pair
    Active_Replicated = ['ActiveReplicated']
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', ModuleCtx.Outage_Seconds)
def test_outage_with_standby_in_sync(ha_pair:'HAEnvironment', outage_seconds:'int') -> 'None':
    """ The active node keeps acknowledging publications while Consul is unavailable and its standby in sync.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    outage_started = time.time()
    env.consul.stop()

    time.sleep(outage_seconds)

    outage_ended = time.time()
    env.consul.resume()

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
    """ With Consul unavailable, the active node cannot mark out a standby that failed, so it acknowledges nothing
    and clients receive errors until Consul returns, after which it continues alone and admits the standby again.
    """
    env = ha_pair

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # Consul becomes unavailable and the standby fails during the outage ..
    env.consul.stop()
    time.sleep(ModuleCtx.Traffic_Seconds)

    standby_failed = time.time()
    standby.kill()

    time.sleep(ModuleCtx.Outage_Seconds[-1])

    # .. so nothing is acknowledged until Consul returns ..
    outage_ended = time.time()

    acknowledged = publisher.get_acknowledged_between(standby_failed + ModuleCtx.In_Flight_Grace, outage_ended)
    assert not acknowledged, f'Acknowledged without the standby and the referee -> {acknowledged}'

    errors = publisher.count_errors_after(standby_failed)
    assert errors > 0, 'No client received an error during the outage'

    # .. after which the active node marks the standby out and continues alone ..
    env.consul.resume()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)
    _ = active.wait_until_server_up(ModuleCtx.Mark_Out_Timeout)

    resumed_at = time.time()
    time.sleep(ModuleCtx.Traffic_Seconds)

    after_outage = publisher.get_acknowledged_between(resumed_at, time.time())
    assert after_outage, 'No publication acknowledged once Consul returned'

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
    """ A Consul recreated without its data holds no record while both nodes have seen a generation,
    so both nodes stop with an error and neither bootstraps a new generation.
    """
    env = ha_pair
    env.consul.recreate_without_data()

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

    record = env.consul.read_record()
    assert record is None, f'A new generation was bootstrapped -> {record}'

# ################################################################################################################################
# ################################################################################################################################
