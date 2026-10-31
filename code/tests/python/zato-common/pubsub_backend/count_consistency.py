# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.counts import Milliseconds_Per_Minute, No_Publisher
from zato.common.pubsub.sql.schema import delivery_table, message_table, publish_count_table, queue_count_table, \
    topic_count_table

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

# How far back the moved messages are published, in milliseconds.
_moved_back_ms = 3 * Milliseconds_Per_Minute

# ################################################################################################################################
# ################################################################################################################################

def _read_rows(table:'Table') -> 'anylist':
    """ Reads all the rows of one table.
    """
    engine = get_pubsub_engine()

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
    """ Reads the count tables, leaving out the rows that dropped to zero.
    """
    queue_counts:'anydict' = {}
    topic_counts:'anydict' = {}
    publish_counts:'anydict' = {}

    for row in _read_rows(queue_count_table):
        assert row.depth >= 0, row
        if row.depth > 0:
            queue_counts[row.sub_key, row.topic_name] = row.depth

    for row in _read_rows(topic_count_table):
        assert row.total >= 0, row
        if row.total > 0:
            topic_counts[row.topic_name] = row.total

    for row in _read_rows(publish_count_table):
        assert row.total >= 0, row
        if row.total > 0:
            publish_counts[row.topic_name, row.minute_ms, row.publisher] = row.total

    out = queue_counts, topic_counts, publish_counts
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

def _move_back(msg_ids:'strlist') -> 'None':
    """ Moves the publication time of the given messages a few minutes back and makes one of them anonymous.
    """
    engine = get_pubsub_engine()

    with engine.begin() as connection:
        for index, msg_id in enumerate(msg_ids):

            update_statement = message_table.update()
            update_statement = update_statement.where(message_table.c.msg_id == msg_id)
            update_statement = update_statement.values(pub_time_ms=message_table.c.pub_time_ms - _moved_back_ms)

            if index == 0:
                update_statement = update_statement.values(publisher=None)

            _ = connection.execute(update_statement)

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

def run_count_consistency_scenario() -> 'None':
    """ The queue, topic and publication counts agree with the rows after every kind of change to them.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
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

    # .. a change of the publication time and of the publisher ..
    _move_back(topic_1_msg_ids[2:4])
    _assert_counts_match(backend, 'move-back')

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
