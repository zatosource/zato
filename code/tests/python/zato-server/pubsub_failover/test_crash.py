# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time
from collections import Counter

# Zato
from failover import docker, read_audit_rows, read_audit_takeovers, read_generation, wait_until_up
from workload import describe_copies, get_attempts_by_msg_id, get_count_mismatches, get_repeats_not_in_flight, Push_Batch_Size, \
    Topic_Name, wait_for_deliveries, Workload
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, is_postgresql_mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FailoverEnvironment
    from failover import ContainerServer
    from zato.common.typing_ import dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_crash')

# ################################################################################################################################
# ################################################################################################################################

# How long the clients publish before each kill and after the last restart, in seconds.
_burst_seconds = 10

# How many times the server is killed.
_kill_count = 2

# The status code of a request that the receiver accepted.
_status_ok = 200

# The push deliveries that the audit log of the server recorded.
_audit_delivered_query = "select msg_id from event where source = 'pubsub' and event_type = 'delivered'"

# ################################################################################################################################
# ################################################################################################################################

def _kill_and_restart(workload:'Workload', server:'ContainerServer') -> 'None':
    """ Kills the server with SIGKILL and starts its container again.
    """
    _ = docker('kill', server.container_name)
    kill_time = time.time()
    workload.fault_windows.append((kill_time, kill_time))
    _ = docker('start', server.container_name)
    _ = wait_until_up(server)

# ################################################################################################################################

def _get_audit_deliveries(server:'ContainerServer', records:'dictlist', msg_ids:'strlist') -> 'tuple[int, strlist]':
    """ Compares the push deliveries that the receiver accepted with those that the audit log recorded,
    for the given messages. Returns how many accepted deliveries the audit log lacks, and each message
    that the audit log records more often than the receiver accepted it.
    """
    wanted = set(msg_ids)
    accepted:'Counter[str]' = Counter()
    audited:'Counter[str]' = Counter()

    for record in records:
        if record['status_code'] == _status_ok and record['msg_id'] in wanted:
            accepted[record['msg_id']] += 1

    for row in read_audit_rows(server, _audit_delivered_query):
        if row[0] in wanted:
            audited[row[0]] += 1

    lost = 0
    surplus:'strlist' = []

    for msg_id, accepted_count in accepted.items():
        audited_count = audited[msg_id]
        if audited_count < accepted_count:
            lost += accepted_count - audited_count
        elif audited_count > accepted_count:
            surplus.append(msg_id)

    out = lost, surplus
    return out

# ################################################################################################################################

def _write_audit_report(lost:'int') -> 'None':
    """ Appends the number of audit events lost per kill to the report of the crash suite.
    """
    directory = os.path.join(get_runtime_dir(), 'reports')
    os.makedirs(directory, exist_ok=True)

    lost_per_kill = lost / _kill_count
    line = f'crash | {time.strftime("%H:%M:%S")} | kills {_kill_count} | audit delivery events lost {lost} | ' + \
        f'per kill {lost_per_kill:.1f}\n'

    with open(os.path.join(directory, f'crash-audit-{get_db_mode()}.txt'), 'a') as report_file:
        _ = report_file.write(line)

# ################################################################################################################################
# ################################################################################################################################

def test_crash_during_bursts(crash_env:'FailoverEnvironment') -> 'None':
    """ A server killed with SIGKILL during publication, pull and push bursts and started again loses no publication
    it acknowledged, hands out a pulled message again only when its acknowledgement failed and repeats push deliveries
    only for those that a kill interrupted.
    """
    env = crash_env
    server = env.server_a

    receiver = env.receivers[Topic_Name]
    receiver.clear_output()

    is_postgresql = is_postgresql_mode(env.database.mode)

    if is_postgresql:
        start_generation = read_generation(env.database)
    else:
        start_generation = 0

    workload = Workload(env, [server])
    workload.start()

    # The clients publish, pull and receive pushes while the server is killed and restarted ..
    try:
        for _ in range(_kill_count):
            time.sleep(_burst_seconds)
            _kill_and_restart(workload, server)

        time.sleep(_burst_seconds)

    finally:
        workload.is_publishing.clear()

    # .. the puller takes and acknowledges what is left once the publishers are done ..
    workload.drain_pulls()

    acknowledged = workload.acknowledged

    logger.info('Acknowledged %d, pulled %d, publish errors %d, failed pulls %d, failed acks %d',
        len(acknowledged), len(workload.pulled), workload.publish_errors, workload.failed_pulls,
        len(workload.failed_ack_msg_ids))

    # Every acknowledged publication was pulled, and only a message whose acknowledgement failed was pulled twice ..
    unexpected = workload.get_unexpected_repeated_pulls()
    assert not unexpected, sorted(unexpected)[:10]

    # .. every acknowledged publication was pushed ..
    delivered = wait_for_deliveries(env, acknowledged)
    copies_by_msg_id = get_attempts_by_msg_id(delivered)

    # .. a kill repeats at most the batch it interrupted ..
    repeated:'strlist' = []

    for msg_id, attempts in copies_by_msg_id.items():
        if len(attempts) > 1:
            repeated.append(msg_id)

    logger.info('Pushed %d, repeated %d', len(delivered), len(repeated))
    assert len(repeated) <= _kill_count * Push_Batch_Size, len(repeated)

    # .. on PostgreSQL, a repeated copy carries a higher attempt number, as the attempts are recorded in the database ..
    if is_postgresql:
        for msg_id in repeated:
            attempts = copies_by_msg_id[msg_id]
            assert len(attempts) == len(set(attempts)), (msg_id, attempts)

    # .. each repeated copy follows a first copy that was received before a kill, which the kill kept
    # .. from being acknowledged, and is itself received after that kill ..
    records = receiver.get_request_records()
    not_in_flight = get_repeats_not_in_flight(records, workload.fault_windows)
    assert not not_in_flight, describe_copies(records, not_in_flight[:10], workload.fault_windows)

    # .. on PostgreSQL, the audit log records each restart as a takeover from the generation before it ..
    if is_postgresql:

        takeovers = read_audit_takeovers(server, start_generation)
        expected_takeovers:'list[tuple[int, int]]' = []

        for kill_index in range(1, _kill_count + 1):
            expected_generation = start_generation + kill_index
            expected_takeovers.append((expected_generation - 1, expected_generation))

        assert takeovers == expected_takeovers, takeovers

    # .. the audit log records each push that the receiver accepted as a delivery event of its own, a repeated one included,
    # .. except for those still in flight at a kill, whose number the report states ..
    lost, surplus = _get_audit_deliveries(server, records, acknowledged)

    logger.info('Audit delivery events lost %d in %d kills', lost, _kill_count)
    _write_audit_report(lost)

    assert not surplus, surplus[:10]
    assert lost <= _kill_count * Push_Batch_Size, lost

    # .. and the stored counts equal the rows.
    assert not get_count_mismatches(env), get_count_mismatches(env)

# ################################################################################################################################
# ################################################################################################################################
