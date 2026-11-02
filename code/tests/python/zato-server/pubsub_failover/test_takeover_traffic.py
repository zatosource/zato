# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# pytest
import pytest

# Zato
from failover import Controller, docker, read_audit_takeovers, reset_pair, wait_for_generation, wait_until_up
from workload import describe_copies, get_attempts_by_msg_id, get_count_mismatches, get_repeats_not_in_flight, Push_Batch_Size, \
    Topic_Name, wait_for_deliveries, Workload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FailoverEnvironment
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_takeover_traffic')

# ################################################################################################################################
# ################################################################################################################################

# How long the clients publish before the active server fails and after the standby took over, in seconds.
_burst_seconds = 10

# How long the controller may take to switch the servers, in seconds.
_switch_timeout_seconds = 300

# How long a server may take to take over the database once its container started, in seconds.
_takeover_timeout_seconds = 180

# The docker command that makes the active server fail - a graceful stop, a SIGKILL and a frozen process.
_fault_commands = ['stop', 'kill', 'pause']

# ################################################################################################################################
# ################################################################################################################################

def _get_event_time(controller:'Controller', name:'str') -> 'float':
    """ Returns when the controller recorded the first event of the given name, in seconds since the epoch.
    """
    for event in controller.read_events():
        if event['event'] == name:
            return event['time']

    raise Exception(f'No event `{name}` in {controller.read_events()}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault_command', _fault_commands)
def test_takeover_under_traffic(failover_env:'FailoverEnvironment', fault_command:'str') -> 'None':
    """ Item 10.11 - the controller replaces the active server while the clients publish, pull and receive pushes.
    No acknowledged publication is lost, a pulled message is handed out again only when its acknowledgement failed,
    and each repeated push was in flight when the active server failed.
    """
    env = failover_env
    generation = reset_pair(env)

    receiver = env.receivers[Topic_Name]
    receiver.clear_output()

    # The clients send their requests to whichever server of the pair answers them ..
    workload = Workload(env, [env.server_a, env.server_b])
    workload.start()

    events_path = os.path.join(env.work_dir, f'controller-traffic-{fault_command}.jsonl')
    controller = Controller(env.server_a, env.server_b, events_path)
    controller.start()

    try:
        time.sleep(_burst_seconds)

        # .. the active server fails during the traffic ..
        _ = docker(fault_command, env.server_a.container_name)
        fault_started = time.time()
        fault_time = time.monotonic()

        # .. the controller starts the standby, which takes over the database, and stops the old server,
        # .. which a frozen server resumes for, so the fault lasts until that stop ..
        controller.wait_for_switch(_switch_timeout_seconds)
        old_stopped = _get_event_time(controller, 'old_stopped')
        workload.fault_windows.append((fault_started, old_stopped))

        _ = wait_until_up(env.server_b)
        _ = wait_for_generation(env.database, generation + 1, _takeover_timeout_seconds)

        logger.info('%s to takeover: %.1fs', fault_command, time.monotonic() - fault_time)

        # .. and the traffic continues on it.
        time.sleep(_burst_seconds)

    finally:
        controller.stop()
        workload.is_publishing.clear()

    # The puller takes and acknowledges what is left once the publishers are done ..
    workload.drain_pulls()

    acknowledged = workload.acknowledged

    logger.info('Acknowledged %d, pulled %d, publish errors %d, failed pulls %d, failed acks %d',
        len(acknowledged), len(workload.pulled), workload.publish_errors, workload.failed_pulls,
        len(workload.failed_ack_msg_ids))

    # .. only a message whose acknowledgement failed was pulled twice ..
    unexpected = workload.get_unexpected_repeated_pulls()
    assert not unexpected, sorted(unexpected)[:10]

    # .. every acknowledged publication was pushed ..
    delivered = wait_for_deliveries(env, acknowledged)
    copies_by_msg_id = get_attempts_by_msg_id(delivered)

    # .. the failure repeats at most the batch it interrupted, each repeated copy with a higher attempt number ..
    repeated:'strlist' = []

    for msg_id, attempts in copies_by_msg_id.items():
        if len(attempts) > 1:
            repeated.append(msg_id)
            assert len(attempts) == len(set(attempts)), (msg_id, attempts)

    logger.info('Pushed %d, repeated %d', len(delivered), len(repeated))
    assert len(repeated) <= Push_Batch_Size, len(repeated)

    # .. each repeated copy follows a first copy that was received before the failure ..
    records = receiver.get_request_records()
    not_in_flight = get_repeats_not_in_flight(records, workload.fault_windows)
    assert not not_in_flight, describe_copies(records, not_in_flight[:10], workload.fault_windows)

    # .. the audit log of the new server records its takeover from the generation of the old one ..
    takeovers = read_audit_takeovers(env.server_b, generation)
    assert takeovers == [(generation, generation + 1)], takeovers

    # .. and the stored counts equal the rows.
    assert not get_count_mismatches(env), get_count_mismatches(env)

# ################################################################################################################################
# ################################################################################################################################
