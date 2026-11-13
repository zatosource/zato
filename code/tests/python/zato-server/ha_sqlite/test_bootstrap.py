# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The pair as it forms - both nodes start together, one becomes active, the other joins it, HAProxy routes
# to the active node only, and the standby copy holds every acknowledged publication, every recorded push attempt
# and every claimed scheduler slot at the moment of its acknowledgment, push or run.

# stdlib
import logging
import time
from http.client import OK
from urllib.request import urlopen

# Zato
from checks import get_starts, read_run_log
from ha_checks import check_copies, check_scheduler, has_message, read_rows, read_run_states
from workload import Topic_Name
from zato.common.test.client import PublishClient
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_, anydict, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.bootstrap')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The roles of a pair that formed
    Role_Active  = 'ActiveReplicated'
    Role_Standby = 'StandbyInSync'
    Link_Streaming = 'Streaming'

    # How many publications the test of the barrier checks one by one
    Publication_Count = 200

    # How long the test of the barrier lets the scheduler run and the pushes arrive, in seconds
    Observation_Seconds = 30

    # How often the receiver and the run logs are read during that time, in seconds
    Poll_Interval = 0.2

    # How long a request through HAProxy may take, in seconds
    Request_Timeout = 5

    # The query of the attempts of one message to each of its subscribers
    Attempt_Query = 'select d.attempt from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
        'where m.msg_id = ?'

    # The query of the number of subscribers of a topic, each of which receives a delivery of each message
    Subscriber_Query = 'select count(*) from pubsub_topic_sub where topic_name = ?'

# ################################################################################################################################
# ################################################################################################################################

def _get_pair(env:'HAEnvironment') -> 'tuple[Node, Node]':
    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    out = (active, standby)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_bootstrap(ha_pair:'HAEnvironment') -> 'None':
    """ One node is active with its standby in sync, both hold the generation of the referee, the referee names them,
    the Zato server runs on the active node only and HAProxy reaches it.
    """
    env = ha_pair
    active, standby = _get_pair(env)

    active_report = active.read_role()
    standby_report = standby.read_role()

    assert active_report is not None
    assert standby_report is not None

    assert active_report['role'] == ModuleCtx.Role_Active, active_report
    assert active_report['link'] == ModuleCtx.Link_Streaming, active_report
    assert standby_report['role'] == ModuleCtx.Role_Standby, standby_report

    record = env.referee.read_record()
    assert record is not None

    assert record['active_node'] == active.node_name, record
    assert record['standby_node'] == standby.node_name, record
    assert record['standby_in_sync'], record

    assert active_report['generation'] == record['generation'], (active_report, record)
    assert standby_report['generation'] == record['generation'], (standby_report, record)

    # The server runs only where the node is active ..
    assert active.is_server_up()
    assert not standby.is_server_up()

    # .. and HAProxy reaches it.
    with urlopen(f'{env.haproxy.base_url}/zato/ping', timeout=ModuleCtx.Request_Timeout) as response:
        assert response.status == OK

# ################################################################################################################################

def _read_attempts(standby:'Node', msg_id:'str') -> 'list[int]':
    """ Returns the attempt of each delivery of a message that the standby copy holds.
    """
    out:'list[int]' = []

    for (attempt,) in read_rows(standby.db_path('pubsub.db'), ModuleCtx.Attempt_Query, [msg_id]):
        out.append(attempt)

    return out

# ################################################################################################################################

def _check_pushes(
    env:'HAEnvironment',
    standby:'Node',
    subscriber_count:'int',
    checked:'set[tuple[str, int]]',
) -> 'strlist':
    """ Checks that each push received since the last call is recorded in the standby copy with its attempt
    or a later one, or that its delivery is gone from the copy, which only a replicated delete achieves,
    as no client pulls during the test.
    """
    out:'strlist' = []
    receiver = env.receivers[Topic_Name]

    for record in receiver.get_request_records():

        key = (record['msg_id'], record['delivery_attempt'])

        if key in checked:
            continue

        checked.add(key)

        attempts = _read_attempts(standby, record['msg_id'])

        if len(attempts) < subscriber_count:
            continue

        if max(attempts) < record['delivery_attempt']:
            out.append(f'{key} recorded with attempts {attempts}')

    return out

# ################################################################################################################################

def _check_claims(env:'HAEnvironment', standby:'Node') -> 'strlist':
    """ Checks that each run that began is counted in the run state of the standby copy.
    """
    out:'strlist' = []

    entries = read_run_log(cast_('any_', env))
    states:'anydict' = read_run_states(standby)

    jobs:'set[str]' = set()

    for entry in get_starts(entries):
        jobs.add(entry['job'])

    for job in sorted(jobs):
        started = len(get_starts(entries, job))

        if job not in states:
            out.append(f'{job} began {started} runs and has no run state on the standby')
            continue

        run_count = states[job]['run_count']

        if run_count < started:
            out.append(f'{job} began {started} runs and has a run count of {run_count} on the standby')

    return out

# ################################################################################################################################

def test_replication_barrier(ha_pair:'HAEnvironment') -> 'None':
    """ The standby copy holds each publication at the moment it is acknowledged, each push attempt at the moment
    the receiver has it, and each scheduler claim at the moment its run begins.
    """
    env = ha_pair
    active, standby = _get_pair(env)

    client = PublishClient(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    missing:'strlist' = []

    rows = read_rows(standby.db_path('pubsub.db'), ModuleCtx.Subscriber_Query, [Topic_Name])
    subscriber_count = rows[0][0]

    # Each acknowledged publication is in the standby copy at once ..
    for index in range(ModuleCtx.Publication_Count):
        result = client.publish(Topic_Name, {'index': index})
        msg_id = result['msg_id']

        if not has_message(standby, msg_id):
            missing.append(msg_id)

    assert not missing, f'Acknowledged and absent from the standby -> {missing}'

    # .. as is each push attempt and each claim of a scheduler slot.
    checked:'set[tuple[str, int]]' = set()
    problems:'strlist' = []
    deadline = time.monotonic() + ModuleCtx.Observation_Seconds

    while time.monotonic() < deadline:
        problems.extend(_check_pushes(env, standby, subscriber_count, checked))
        problems.extend(_check_claims(env, standby))
        time.sleep(ModuleCtx.Poll_Interval)

    assert not problems, problems
    assert checked, 'No push was received'

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
