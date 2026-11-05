# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The clients that publish and pull while servers are killed, stopped, frozen or replaced, and the checks
# of what they observed against the pub/sub database and the push receiver.

# stdlib
import sqlite3
import threading
import time
from collections import Counter

# Zato
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

# The topic of the workload, which has a pull subscriber and a push subscriber.
Topic_Name = 'iam.user.created'

# How many messages one push batch holds, which is how many copies one fault may repeat at most.
Push_Batch_Size = 50

# How many clients publish at the same time.
_publisher_count = 8

# How many messages one pull asks for.
_pull_max_messages = 100

# How long a client waits after a failed request before the next one, in seconds.
_retry_pause_seconds = 0.2

# How long the push deliveries may take to reach the receiver once the publishers stopped, in seconds.
_delivery_timeout_seconds = 300

# How often the receiver and the database are checked, in seconds.
_poll_seconds = 1.0

# The status code of a request that the receiver accepted.
_status_ok = 200

# How long after the recorded time of a fault a server may still have sent a request, in seconds -
# the time is taken once the docker command returns.
_fault_time_tolerance = 1.0

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

class Workload:
    """ The clients that publish and pull while servers fail, with what each one observed. Each client sends its requests
    to the server that answered its previous request and turns to the next server of the list after a failed one.
    """

    def __init__(self, env:'FailoverEnvironment', servers:'list[ContainerServer]') -> 'None':
        self.env = env
        self.servers = servers
        self.lock = threading.Lock()

        self.is_publishing = threading.Event()
        self.is_pulling = threading.Event()

        # What the servers acknowledged to the publishers and handed out to the puller, with the puller's queue.
        self.acknowledged:'strlist' = []
        self.pulled:'strlist' = []
        self.sub_key = ''

        # How many pulls failed, and the messages whose acknowledgement failed, which are the only ones
        # that a later pull may hand out again.
        self.failed_pulls = 0
        self.failed_ack_msg_ids:'set[str]' = set()

        # When each fault began and when the failed server stopped for good, in seconds since the epoch,
        # which the receiver's request times are compared with. A frozen server resumes when it is stopped,
        # so it may still send what it had prepared until then.
        self.fault_windows:'list[tuple[float, float]]' = []

        self.publish_errors = 0
        self._threads:'list[threading.Thread]' = []

# ################################################################################################################################

    def _publish_loop(self) -> 'None':

        clients:'list[PublishClient]' = []
        for server in self.servers:
            clients.append(PublishClient(server.base_url, self.env.publisher_username, self.env.publisher_password))

        position = 0
        index = 0

        while self.is_publishing.is_set():
            index += 1
            try:
                result = clients[position].publish(Topic_Name, {'workload_index': index})
            except Exception:
                with self.lock:
                    self.publish_errors += 1
                position = (position + 1) % len(clients)
                time.sleep(_retry_pause_seconds)
            else:
                with self.lock:
                    self.acknowledged.append(result['msg_id'])

# ################################################################################################################################

    def _pull_loop(self) -> 'None':

        clients:'list[PullClient]' = []
        for server in self.servers:
            clients.append(PullClient(server.base_url, self.env.puller_username, self.env.puller_password))

        position = 0

        while self.is_pulling.is_set():
            client = clients[position]

            try:
                result = client.pull(max_messages=_pull_max_messages, needs_ack=False)
            except Exception:
                with self.lock:
                    self.failed_pulls += 1
                position = (position + 1) % len(clients)
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
                position = (position + 1) % len(clients)
                time.sleep(_retry_pause_seconds)

# ################################################################################################################################

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

# ################################################################################################################################

    def stop(self) -> 'None':
        self.is_publishing.clear()
        self.is_pulling.clear()

        for thread in self._threads:
            thread.join()

# ################################################################################################################################

    def drain_pulls(self) -> 'None':
        """ Stops the publishers and lets the puller take and acknowledge what is left, including the messages
        of pulls whose response a fault cut off, which their lease hands out again, then stops the puller.
        """
        self.is_publishing.clear()

        deadline = time.monotonic() + _delivery_timeout_seconds

        while True:
            with self.lock:
                not_pulled = set(self.acknowledged) - set(self.pulled)

            if not not_pulled and not get_pending_msg_ids(self.env, self.sub_key):
                break

            assert time.monotonic() < deadline, f'Pull queue not drained, not pulled {len(not_pulled)}'
            time.sleep(_poll_seconds)

        self.stop()

# ################################################################################################################################

    def get_unexpected_repeated_pulls(self) -> 'set[str]':
        """ Returns each message pulled more than once whose acknowledgement never failed.
        """
        pulled_counts = Counter(self.pulled)
        repeated_pulls:'set[str]' = set()

        for msg_id, count in pulled_counts.items():
            if count > 1:
                repeated_pulls.add(msg_id)

        out = repeated_pulls - self.failed_ack_msg_ids
        return out

# ################################################################################################################################
# ################################################################################################################################

def read_rows(env:'FailoverEnvironment', query:'str') -> 'list':
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

def get_count_mismatches(env:'FailoverEnvironment') -> 'strlist':
    """ Returns each key whose stored count differs from the number of its rows.
    """
    out:'strlist' = []

    for name, raw_query, stored_query in _count_queries:

        raw:'anydict' = {}
        stored:'anydict' = {}

        for row in read_rows(env, raw_query):
            raw[tuple(row[:-1])] = int(row[-1])

        for row in read_rows(env, stored_query):
            value = int(row[-1])
            if value:
                stored[tuple(row[:-1])] = value

        if raw != stored:
            out.append(f'{name}: {stored} stored, {raw} rows')

    return out

# ################################################################################################################################

def get_pending_msg_ids(env:'FailoverEnvironment', sub_key:'str') -> 'set[str]':
    """ Returns the identifiers of the messages that wait in the queue of one subscriber.
    """
    query = 'select m.msg_id from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
        f"where d.sub_key = '{sub_key}'"

    out:'set[str]' = set()
    for row in read_rows(env, query):
        out.add(row[0])

    return out

# ################################################################################################################################

def get_repeats_not_in_flight(records:'dictlist', fault_windows:'list[tuple[float, float]]') -> 'strlist':
    """ Returns each msg_id received successfully more than once without a fault between its first copy
    and the next one, which no fault accounts for.
    """
    times_by_msg_id:'dict[str, list[float]]' = {}

    for record in records:
        if record['status_code'] != _status_ok:
            continue
        msg_id = record['msg_id']
        if msg_id not in times_by_msg_id:
            times_by_msg_id[msg_id] = []
        times_by_msg_id[msg_id].append(record['time'])

    out:'strlist' = []

    for msg_id, times in times_by_msg_id.items():
        for first_time, next_time in zip(times, times[1:]):
            if not _is_fault_between(fault_windows, first_time, next_time):
                out.append(msg_id)
                break

    return out

# ################################################################################################################################

def describe_copies(records:'dictlist', msg_ids:'strlist', fault_windows:'list[tuple[float, float]]') -> 'str':
    """ Returns the time, the status code and the attempt number of each request for the given messages,
    together with the windows of the faults, for the message of a failed assertion.
    """
    wanted = set(msg_ids)
    copies:'dict[str, list[tuple[float, int, int]]]' = {}

    for record in records:
        msg_id = record['msg_id']
        if msg_id in wanted:
            if msg_id not in copies:
                copies[msg_id] = []
            copies[msg_id].append((record['time'], record['status_code'], record['delivery_attempt']))

    out = f'faults {fault_windows}, copies {copies}'
    return out

# ################################################################################################################################

def _is_fault_between(fault_windows:'list[tuple[float, float]]', start:'float', end:'float') -> 'bool':
    """ Tells whether a first copy received at start was received before a fault ended and the next copy,
    received at end, after the fault began.
    """
    for fault_start, fault_end in fault_windows:
        if start <= fault_end + _fault_time_tolerance and fault_start <= end:
            return True
    return False

# ################################################################################################################################

def wait_for_deliveries(env:'FailoverEnvironment', msg_ids:'strlist') -> 'dictlist':
    """ Waits until the push receiver has every one of the given messages and returns what it received.
    """
    receiver = env.receivers[Topic_Name]
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

def get_attempts_by_msg_id(delivered:'dictlist') -> 'dict[str, list[int]]':
    """ Returns the attempt number of each copy that the receiver has, by msg_id.
    """
    out:'dict[str, list[int]]' = {}

    for message in delivered:
        msg_id = message['msg_id']
        if msg_id not in out:
            out[msg_id] = []
        out[msg_id].append(message['delivery_attempt'])

    return out

# ################################################################################################################################
# ################################################################################################################################
