# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import sqlite3
import threading
import time
from collections import Counter

# Zato
from failover import docker, wait_until_up
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.pubsub_database import connect, is_postgresql_mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import FailoverEnvironment
    from failover import ContainerServer
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_crash')

# ################################################################################################################################
# ################################################################################################################################

# The topic of the test, which has a pull subscriber and a push subscriber.
_topic_name = 'iam.user.created'

# How many clients publish at the same time.
_publisher_count = 8

# How long the clients publish before each kill and after the last restart, in seconds.
_burst_seconds = 10

# How many times the server is killed.
_kill_count = 2

# How many messages one pull asks for.
_pull_max_messages = 100

# How long a client waits after a failed request before the next one, in seconds.
_retry_pause_seconds = 0.2

# How long the push deliveries may take to reach the receiver after the last restart, in seconds.
_delivery_timeout_seconds = 300

# How often the receiver is checked, in seconds.
_poll_seconds = 1.0

# How many messages one push batch holds, which is how many copies a kill may repeat at most.
_push_batch_size = 50

# The raw counts and the stored counts that must equal them.
_count_queries = [
    ('queue',
        'select sub_key, topic_name, count(*) from pubsub_delivery group by sub_key, topic_name',
        'select sub_key, topic_name, sum(depth) from pubsub_queue_count group by sub_key, topic_name'),
    ('topic',
        'select topic_name, count(*) from pubsub_message group by topic_name',
        'select topic_name, sum(total) from pubsub_topic_count group by topic_name'),
]

# ################################################################################################################################
# ################################################################################################################################

class _Workload:
    """ The clients that publish and pull while the server is killed and restarted, with what each one observed.
    """

    def __init__(self, env:'FailoverEnvironment', server:'ContainerServer') -> 'None':
        self.env = env
        self.server = server
        self.lock = threading.Lock()

        self.is_publishing = threading.Event()
        self.is_pulling = threading.Event()

        # What the server acknowledged to the publishers and handed out to the puller, with the puller's queue.
        self.acknowledged:'strlist' = []
        self.pulled:'strlist' = []
        self.sub_key = ''

        # How many pulls failed, and the messages whose acknowledgement failed, which are the only ones
        # that a later pull may hand out again.
        self.failed_pulls = 0
        self.failed_ack_msg_ids:'set[str]' = set()

        self.publish_errors = 0
        self._threads:'list[threading.Thread]' = []

    def _publish_loop(self) -> 'None':
        client = PublishClient(self.server.base_url, self.env.publisher_username, self.env.publisher_password)
        index = 0

        while self.is_publishing.is_set():
            index += 1
            try:
                result = client.publish(_topic_name, {'crash_test_index': index})
            except Exception:
                with self.lock:
                    self.publish_errors += 1
                time.sleep(_retry_pause_seconds)
            else:
                with self.lock:
                    self.acknowledged.append(result['msg_id'])

    def _pull_loop(self) -> 'None':
        client = PullClient(self.server.base_url, self.env.puller_username, self.env.puller_password)

        while self.is_pulling.is_set():
            try:
                result = client.pull(max_messages=_pull_max_messages, needs_ack=False)
            except Exception:
                with self.lock:
                    self.failed_pulls += 1
                time.sleep(_retry_pause_seconds)
                continue

            msg_ids:'strlist' = []

            with self.lock:
                for message in result['messages']:
                    meta = message['meta']
                    self.sub_key = meta['sub_key']
                    msg_ids.append(meta['msg_id'])
                    self.pulled.append(meta['msg_id'])

            if not msg_ids:
                continue

            try:
                _ = client.ack(msg_ids)
            except Exception:
                with self.lock:
                    self.failed_ack_msg_ids.update(msg_ids)
                time.sleep(_retry_pause_seconds)

    def start(self) -> 'None':
        self.is_publishing.set()
        self.is_pulling.set()

        for _ in range(_publisher_count):
            thread = threading.Thread(target=self._publish_loop, daemon=True)
            thread.start()
            self._threads.append(thread)

        thread = threading.Thread(target=self._pull_loop, daemon=True)
        thread.start()
        self._threads.append(thread)

    def stop(self) -> 'None':
        self.is_publishing.clear()
        self.is_pulling.clear()

        for thread in self._threads:
            thread.join()

    def kill_and_restart(self) -> 'None':
        """ Kills the server with SIGKILL and starts its container again.
        """
        _ = docker('kill', self.server.container_name)
        _ = docker('start', self.server.container_name)
        _ = wait_until_up(self.server)

# ################################################################################################################################
# ################################################################################################################################

def _read_rows(env:'FailoverEnvironment', query:'str') -> 'list':
    """ Returns the rows of a query against the pub/sub database of the environment, whichever database it is.
    """
    database = env.database

    if is_postgresql_mode(database.mode):
        connection = connect(database)
    else:
        connection = sqlite3.connect(database.env['Zato_PubSub_DB_Path'])

    try:
        cursor = connection.cursor()
        _ = cursor.execute(query)
        out = list(cursor.fetchall())
    finally:
        connection.close()

    return out

# ################################################################################################################################

def _get_count_mismatches(env:'FailoverEnvironment') -> 'strlist':
    """ Returns each key whose stored count differs from the number of its rows.
    """
    out:'strlist' = []

    for name, raw_query, stored_query in _count_queries:

        raw:'anydict' = {}
        stored:'anydict' = {}

        for row in _read_rows(env, raw_query):
            raw[tuple(row[:-1])] = int(row[-1])

        for row in _read_rows(env, stored_query):
            value = int(row[-1])
            if value:
                stored[tuple(row[:-1])] = value

        if raw != stored:
            out.append(f'{name}: {stored} stored, {raw} rows')

    return out

# ################################################################################################################################

def _get_pending_msg_ids(env:'FailoverEnvironment', sub_key:'str') -> 'set[str]':
    """ Returns the identifiers of the messages that wait in the queue of one subscriber.
    """
    query = 'select m.msg_id from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
        f"where d.sub_key = '{sub_key}'"

    out:'set[str]' = set()
    for row in _read_rows(env, query):
        out.add(row[0])

    return out

# ################################################################################################################################

def _wait_for_deliveries(env:'FailoverEnvironment', msg_ids:'strlist') -> 'dictlist':
    """ Waits until the push receiver has every one of the given messages and returns what it received.
    """
    receiver = env.receivers[_topic_name]
    expected = set(msg_ids)
    deadline = time.monotonic() + _delivery_timeout_seconds

    while True:

        delivered = receiver.get_delivered_messages()

        received:'set[str]' = set()
        for message in delivered:
            received.add(message['msg_id'])

        missing = expected - received

        if not missing:
            return delivered

        assert time.monotonic() < deadline, f'Not delivered: {len(missing)} of {len(expected)}'
        time.sleep(_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################

def test_crash_during_bursts(crash_env:'FailoverEnvironment') -> 'None':
    """ A server killed with SIGKILL during publication, pull and push bursts and started again loses no publication
    it acknowledged, hands out a pulled message again only when its acknowledgement failed and repeats push deliveries
    only for those that a kill interrupted.
    """
    env = crash_env
    server = env.server_a

    receiver = env.receivers[_topic_name]
    receiver.clear_output()

    workload = _Workload(env, server)
    workload.start()

    # The clients publish, pull and receive pushes while the server is killed and restarted ..
    try:
        for _ in range(_kill_count):
            time.sleep(_burst_seconds)
            workload.kill_and_restart()

        time.sleep(_burst_seconds)

    finally:
        workload.is_publishing.clear()

    # .. the puller takes and acknowledges what is left once the publishers are done, including the messages
    # .. of pulls whose response a kill cut off, which their lease hands out again ..
    deadline = time.monotonic() + _delivery_timeout_seconds

    while True:
        with workload.lock:
            not_pulled = set(workload.acknowledged) - set(workload.pulled)

        if not not_pulled and not _get_pending_msg_ids(env, workload.sub_key):
            break

        assert time.monotonic() < deadline, f'Pull queue not drained, not pulled {len(not_pulled)}'
        time.sleep(_poll_seconds)

    workload.stop()

    acknowledged = workload.acknowledged
    pulled = workload.pulled

    logger.info('Acknowledged %d, pulled %d, publish errors %d, failed pulls %d, failed acks %d',
        len(acknowledged), len(pulled), workload.publish_errors, workload.failed_pulls, len(workload.failed_ack_msg_ids))

    # Every acknowledged publication was pulled, and only a message whose acknowledgement failed was pulled twice ..
    pulled_counts = Counter(pulled)
    repeated_pulls:'set[str]' = set()

    for msg_id, count in pulled_counts.items():
        if count > 1:
            repeated_pulls.add(msg_id)

    logger.info('Repeated pulls %d', len(repeated_pulls))
    unexpected = repeated_pulls - workload.failed_ack_msg_ids
    assert not unexpected, sorted(unexpected)[:10]

    # .. every acknowledged publication was pushed ..
    delivered = _wait_for_deliveries(env, acknowledged)

    copies_by_msg_id:'dict[str, list[int]]' = {}

    for message in delivered:
        msg_id = message['msg_id']
        if msg_id not in copies_by_msg_id:
            copies_by_msg_id[msg_id] = []
        copies_by_msg_id[msg_id].append(message['delivery_attempt'])

    # .. a kill repeats at most the batch it interrupted ..
    repeated:'strlist' = []

    for msg_id, attempts in copies_by_msg_id.items():
        if len(attempts) > 1:
            repeated.append(msg_id)

    logger.info('Pushed %d, repeated %d', len(delivered), len(repeated))
    assert len(repeated) <= _kill_count * _push_batch_size, len(repeated)

    # .. on PostgreSQL, a repeated copy carries a higher attempt number, as the attempts are recorded in the database ..
    if is_postgresql_mode(env.database.mode):
        for msg_id in repeated:
            attempts = copies_by_msg_id[msg_id]
            assert len(attempts) == len(set(attempts)), (msg_id, attempts)

    # .. and the stored counts equal the rows.
    assert not _get_count_mismatches(env), _get_count_mismatches(env)

# ################################################################################################################################
# ################################################################################################################################
