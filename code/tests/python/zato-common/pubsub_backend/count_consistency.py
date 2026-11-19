# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.counts import Milliseconds_Per_Minute, No_Publisher
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.schema import delivery_table, message_table, publish_count_table, queue_count_table, \
    topic_count_table
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics, subscribers and publishers the consistency assertions share.
_topic_1 = 'pubsub.backend.test.counts.1'
_topic_2 = 'pubsub.backend.test.counts.2'
_topic_3 = 'pubsub.backend.test.counts.3'
_topic_renamed = 'pubsub.backend.test.counts.renamed'

_sub_key_1 = 'zpsk.test.counts.1'
_sub_key_2 = 'zpsk.test.counts.2'
_sub_key_3 = 'zpsk.test.counts.3'

_publisher_1 = 'alice'
_publisher_2 = 'bob'

# How far back the earlier messages are published, in milliseconds.
_moved_back_ms = 3 * Milliseconds_Per_Minute

# The time of publication of the messages whose counts are expected literally, and the minute that it falls in
_literal_pub_time_iso = '2026-03-01T10:15:30.250000+00:00'
_literal_minute_ms = 1772360100000

# ################################################################################################################################
# ################################################################################################################################

def _read_rows(table:'Table') -> 'anylist':
    """ Reads all the rows of one table.
    """
    engine = get_database_engine()

    with engine.connect() as connection:
        out = connection.execute(select(table)).fetchall()

    return out

# ################################################################################################################################

def _add(counts:'anydict', key:'any_', value:'int') -> 'None':
    """ Adds a value to the count under the given key.
    """
    if key not in counts:
        counts[key] = 0

    counts[key] += value

# ################################################################################################################################

def _get_raw_counts() -> 'tuple[anydict, anydict, anydict]':
    """ Counts the delivery rows of each queue, the message rows of each topic and the publications
    of each topic, minute and publisher straight from the rows themselves.
    """
    queue_counts:'anydict' = {}
    topic_counts:'anydict' = {}
    publish_counts:'anydict' = {}

    for row in _read_rows(delivery_table):
        _add(queue_counts, (row.sub_key, row.topic_name), 1)

    for row in _read_rows(message_table):

        _add(topic_counts, row.topic_name, 1)

        minute_ms = row.pub_time_ms - row.pub_time_ms % Milliseconds_Per_Minute

        if row.publisher is None:
            publisher = No_Publisher
        else:
            publisher = row.publisher

        _add(publish_counts, (row.topic_name, minute_ms, publisher), 1)

    out = queue_counts, topic_counts, publish_counts
    return out

# ################################################################################################################################

def _get_stored_counts() -> 'tuple[anydict, anydict, anydict]':
    """ Reads the count tables, adding up the rows of each key - one on SQLite, any number of change rows
    on PostgreSQL - and leaving out the keys that dropped to zero.
    """
    queue_sums:'anydict' = {}
    topic_sums:'anydict' = {}
    publish_sums:'anydict' = {}

    for row in _read_rows(queue_count_table):
        _add(queue_sums, (row.sub_key, row.topic_name), row.depth)

    for row in _read_rows(topic_count_table):
        _add(topic_sums, row.topic_name, row.total)

    for row in _read_rows(publish_count_table):
        _add(publish_sums, (row.topic_name, row.minute_ms, row.publisher), row.total)

    out:'tuple[anydict, anydict, anydict]' = ({}, {}, {})

    for sums, counts in zip((queue_sums, topic_sums, publish_sums), out):
        for key, value in sums.items():
            assert value >= 0, (key, value)
            if value > 0:
                counts[key] = value

    return out

# ################################################################################################################################

def _assert_counts_match(backend:'SQLPubSubBackend', step:'str') -> 'None':
    """ The count tables agree with the rows they count, and so do the statistics read from them.
    """
    raw_queue_counts, raw_topic_counts, raw_publish_counts = _get_raw_counts()
    stored_queue_counts, stored_topic_counts, stored_publish_counts = _get_stored_counts()

    assert stored_queue_counts == raw_queue_counts, (step, stored_queue_counts, raw_queue_counts)
    assert stored_topic_counts == raw_topic_counts, (step, stored_topic_counts, raw_topic_counts)
    assert stored_publish_counts == raw_publish_counts, (step, stored_publish_counts, raw_publish_counts)

    # The topics with messages are those that have any message rows ..
    topics_with_messages = backend.get_topics_with_messages()
    assert sorted(topics_with_messages) == sorted(raw_topic_counts), (step, topics_with_messages)

    # .. and the per-pair totals are those of the rows.
    for sub_key, topic_name in raw_queue_counts:
        pending_count = backend.get_total_count(sub_key, topic_name, 'pending')
        assert pending_count == raw_queue_counts[sub_key, topic_name], (step, sub_key, topic_name, pending_count)

# ################################################################################################################################

def _publish_earlier(backend:'SQLPubSubBackend', topic_name:'str') -> 'None':
    """ Publishes two messages at an earlier publication time, of which the first one has no publisher.
    """
    now = utcnow()
    pub_time = now - timedelta(milliseconds=_moved_back_ms)
    pub_time_iso = pub_time.isoformat()

    _ = backend.publish(topic_name, 'counts-earlier-0', publisher=None, pub_time=pub_time_iso)
    _ = backend.publish(topic_name, 'counts-earlier-1', publisher=_publisher_1, pub_time=pub_time_iso)

# ################################################################################################################################

def _publish(backend:'SQLPubSubBackend', topic_name:'str', count:'int', publisher:'str | None') -> 'strlist':
    """ Publishes the given number of messages to one topic and returns their identifiers.
    """
    out:'strlist' = []

    for index in range(count):
        result = backend.publish(topic_name, f'counts-message-{index}', publisher=publisher)
        out.append(result.msg_id)

    return out

# ################################################################################################################################

def _assert_stored_counts(step:'str', queue_counts:'anydict', topic_counts:'anydict', publish_counts:'anydict') -> 'None':
    """ The count tables hold exactly the given counts.
    """
    stored_queue_counts, stored_topic_counts, stored_publish_counts = _get_stored_counts()

    assert stored_queue_counts == queue_counts, (step, stored_queue_counts, queue_counts)
    assert stored_topic_counts == topic_counts, (step, stored_topic_counts, topic_counts)
    assert stored_publish_counts == publish_counts, (step, stored_publish_counts, publish_counts)

# ################################################################################################################################

def _get_msg_ids(messages:'anylist', topic_name:'str') -> 'strlist':
    """ Returns the identifiers of the messages of one topic among the messages of a pull.
    """
    out:'strlist' = []

    for message in messages:
        if message['topic_name'] == topic_name:
            out.append(message['msg_id'])

    return out

# ################################################################################################################################

def _run_literal_counts() -> 'None':
    """ The count tables hold the literal counts after each kind of write of the pub/sub commits.
    """
    delete_all_rows()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_2, _topic_1)
    backend.subscribe(_sub_key_1, _topic_2)

    # Publications with and without a publisher ..
    first = backend.publish(_topic_1, 'counts-literal-0', publisher=_publisher_1, pub_time=_literal_pub_time_iso)
    second = backend.publish(_topic_1, 'counts-literal-1', publisher=_publisher_1, pub_time=_literal_pub_time_iso)
    _ = backend.publish(_topic_2, 'counts-literal-2', pub_time=_literal_pub_time_iso)

    queue_counts = {(_sub_key_1, _topic_1): 2, (_sub_key_2, _topic_1): 2, (_sub_key_1, _topic_2): 1}
    topic_counts = {_topic_1: 2, _topic_2: 1}
    publish_counts = {(_topic_1, _literal_minute_ms, _publisher_1): 2, (_topic_2, _literal_minute_ms, No_Publisher): 1}

    _assert_stored_counts('publish', queue_counts, topic_counts, publish_counts)

    # .. an acknowledgement ..
    _ = backend.ack_messages(_sub_key_1, [first.msg_id])

    queue_counts[_sub_key_1, _topic_1] = 1
    _assert_stored_counts('ack', queue_counts, topic_counts, publish_counts)

    # .. a pull, which leases what it hands out and changes no count ..
    messages = backend.pull_messages(_sub_key_1)

    assert _get_msg_ids(messages, _topic_1) == [second.msg_id]
    _assert_stored_counts('pull', queue_counts, topic_counts, publish_counts)

    # .. a fenced acknowledgement with a receipt of its own publisher ..
    topic_2_msg_ids = _get_msg_ids(messages, _topic_2)
    consumed = [(topic_2_msg_ids[0], 1)]

    receipt = build_publication(backend, _topic_1, 'counts-literal-receipt', publisher=_publisher_2,
        pub_time=_literal_pub_time_iso)

    _ = backend.ack_pulled_with_publications(_sub_key_1, consumed, [receipt])

    del queue_counts[_sub_key_1, _topic_2]
    queue_counts[_sub_key_1, _topic_1] = 2
    queue_counts[_sub_key_2, _topic_1] = 3
    topic_counts[_topic_1] = 3
    publish_counts[_topic_1, _literal_minute_ms, _publisher_2] = 1

    _assert_stored_counts('fenced-ack', queue_counts, topic_counts, publish_counts)

    # .. push attempts, which change no count ..
    fetched = backend.fetch_messages(_sub_key_2)
    _ = backend.record_attempts(fetched)

    _assert_stored_counts('attempts', queue_counts, topic_counts, publish_counts)

    # .. and the acknowledgement of every message of a queue, whose fully delivered messages remain as traces.
    fetched_msg_ids = _get_msg_ids(fetched, _topic_1)
    _ = backend.ack_messages(_sub_key_2, fetched_msg_ids)

    del queue_counts[_sub_key_2, _topic_1]
    _assert_stored_counts('ack-all', queue_counts, topic_counts, publish_counts)

# ################################################################################################################################

def run_count_consistency_scenario() -> 'None':
    """ The queue, topic and publication counts agree with the rows after every kind of change to them,
    and they hold the literal counts of each kind of write.
    """
    _run_literal_counts()
    delete_all_rows()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())
    _assert_counts_match(backend, 'empty')

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_2, _topic_1)
    backend.subscribe(_sub_key_2, _topic_2)
    backend.subscribe(_sub_key_3, _topic_2)

    # Publications with and without publishers, and to a topic without subscribers ..
    topic_1_msg_ids = _publish(backend, _topic_1, 5, _publisher_1)
    topic_2_msg_ids = _publish(backend, _topic_2, 3, _publisher_2)

    _ = _publish(backend, _topic_1, 2, None)
    _ = _publish(backend, _topic_3, 2, _publisher_1)

    _assert_counts_match(backend, 'publish')

    # .. acknowledgements ..
    _ = backend.ack_messages(_sub_key_1, topic_1_msg_ids[:2])
    _ = backend.ack_message(_sub_key_2, topic_2_msg_ids[0])
    _assert_counts_match(backend, 'ack')

    # .. publications at an earlier time, with and without a publisher ..
    _publish_earlier(backend, _topic_1)
    _assert_counts_match(backend, 'publish-earlier')

    # .. a queue cleared ..
    _ = backend.clear_queue(_sub_key_3)
    _assert_counts_match(backend, 'clear-queue')

    # .. an unsubscription ..
    backend.unsubscribe(_sub_key_2, _topic_2)
    _assert_counts_match(backend, 'unsubscribe')

    # .. a message deleted from a queue ..
    _ = backend.delete_message(_sub_key_1, _topic_1, topic_1_msg_ids[4])
    _assert_counts_match(backend, 'delete-message')

    # .. a topic renamed ..
    backend.rename_topic(_topic_1, _topic_renamed)
    _assert_counts_match(backend, 'rename-topic')

    # .. a topic deleted ..
    backend.delete_topic(_topic_2)
    _assert_counts_match(backend, 'delete-topic')

    # .. and the cleanup removes the count rows that dropped to zero, without changing what they count.
    cleanup = PubSubCleanup()
    counts = cleanup.sweep_once()

    assert counts['empty_counts'] > 0, counts
    _assert_counts_match(backend, 'cleanup')

    for table, column_name in ((queue_count_table, 'depth'), (topic_count_table, 'total'), (publish_count_table, 'total')):
        for row in _read_rows(table):
            assert row._mapping[column_name] > 0, (table.name, row)

# ################################################################################################################################
# ################################################################################################################################
