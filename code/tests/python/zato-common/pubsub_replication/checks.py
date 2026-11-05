# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks that the replication suites run against whichever server is the primary at the end of a test.

# stdlib
import sqlite3
from collections import Counter
from time import monotonic

# Zato
from zato.common.test.pubsub_database import PubSubDBMode
from zato.common.test.pubsub_replication import connect_active

# local
from workload import Pull_Sub_Key, Pull_Topic, Push_Sub_Key, Push_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_replication import ReplicatedDatabase
    from zato.common.typing_ import any_, anydict, strlist
    from workload import Workload

# ################################################################################################################################
# ################################################################################################################################

def _connect(database:'ReplicatedDatabase') -> 'any_':
    """ Opens a connection to the SQLite file of the test or to whichever PostgreSQL server is the primary now.
    """
    if database.mode == PubSubDBMode.SQLite:
        out = sqlite3.connect(database.env['Zato_PubSub_DB_Path'])
    else:
        out = connect_active(database)

    return out

# ################################################################################################################################

def _fetch_all(database:'ReplicatedDatabase', query:'str') -> 'list':
    connection = _connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        out = list(cursor.fetchall())
    finally:
        connection.close()

    return out

# ################################################################################################################################

def stored_msg_ids(database:'ReplicatedDatabase') -> 'set[str]':
    """ The msg_id of every message row on the primary.
    """
    out:'set[str]' = set()

    for row in _fetch_all(database, 'select msg_id from pubsub_message'):
        out.add(row[0])

    return out

# ################################################################################################################################

def pending_msg_ids(database:'ReplicatedDatabase', sub_key:'str') -> 'set[str]':
    """ The msg_id of every message still in the queue of one subscriber.
    """
    query = 'select m.msg_id from pubsub_delivery d join pubsub_message m on m.id = d.message_id ' + \
        f"where d.sub_key = '{sub_key}'"

    out:'set[str]' = set()

    for row in _fetch_all(database, query):
        out.add(row[0])

    return out

# ################################################################################################################################

def read_generation(database:'ReplicatedDatabase') -> 'int':
    rows = _fetch_all(database, 'select generation from pubsub_active where id = 1')
    out = rows[0][0]
    return out

# ################################################################################################################################

def raise_generation(database:'ReplicatedDatabase') -> 'int':
    """ Raises the generation the way the startup of another server does and returns the new value.
    """
    connection = _connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute('update pubsub_active set generation = generation + 1 where id = 1 returning generation')
        row = cursor.fetchone()
        connection.commit()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def check_counts_equal_rows(database:'ReplicatedDatabase', workload:'Workload') -> 'None':
    """ The queue depths that the counts report equal the delivery rows of each subscriber.
    """
    pairs = [(Pull_Sub_Key, Pull_Topic), (Push_Sub_Key, Push_Topic)]
    depths = workload.backend.get_pending_depths(pairs)

    for sub_key, _ in pairs:
        rows = pending_msg_ids(database, sub_key)
        assert depths[sub_key] == len(rows), f'{sub_key} depth {depths[sub_key]} != rows {len(rows)}'

# ################################################################################################################################

def check_delivery(database:'ReplicatedDatabase', workload:'Workload', restore_time:'float') -> 'anydict':
    """ Checks that no acknowledged publication was lost, that only a message whose acknowledgement failed was pulled
    twice, that each publication has one message row, and returns the measurements of the fault.
    """
    stored = stored_msg_ids(database)
    acknowledged = set(workload.acknowledged)

    # Every acknowledged publication that the database did not lose exists on the primary, once, since msg_id is unique ..
    lost = acknowledged - stored

    # .. a message was handed out to the partner twice only if the partner's acknowledgement of it failed,
    # .. or, with asynchronous replication, if the standby never received the acknowledgement ..
    pulled_counts = Counter(workload.pulled)
    duplicate_pulls:'strlist' = []

    for msg_id, count in pulled_counts.items():
        if count > 1:
            duplicate_pulls.append(msg_id)

    unexpected_duplicates = set(duplicate_pulls) - workload.failed_ack_msg_ids

    if database.is_sync:
        assert not unexpected_duplicates, f'Pulled more than once: {sorted(unexpected_duplicates)[:10]}'

    # .. every pull publication reached the partner, including those of pulls whose response was lost ..
    not_pulled = workload.acknowledged_on(Pull_Topic) - lost - set(workload.pulled)
    assert not not_pulled, f'Not pulled: {sorted(not_pulled)[:10]}'

    # .. and none of them is left in the queue, the partner having acknowledged each of them.
    still_pending = pending_msg_ids(database, Pull_Sub_Key)
    assert not still_pending, f'Pulled and still pending: {sorted(still_pending)[:10]}'

    # Every push publication reached the subscriber, some of them more than once.
    pushed_counts = Counter(workload.pushed)
    not_pushed = workload.acknowledged_on(Push_Topic) - lost - set(pushed_counts)
    assert not not_pushed, f'Not pushed: {sorted(not_pushed)[:10]}'

    repeated_pushes = 0
    for count in pushed_counts.values():
        repeated_pushes += count - 1

    out = {
        'acknowledged': len(acknowledged),
        'lost': len(lost),
        'lost_sample': sorted(lost)[:5],
        'repeated_pulls': len(duplicate_pulls),
        'repeated_pulls_after_lost_acks': len(unexpected_duplicates),
        'failed_pulls': workload.failed_pulls,
        'failed_acks': len(workload.failed_ack_msg_ids),
        'repeated_pushes': repeated_pushes,
        'repeated_publications': len(workload.repeated_publications),
        'publish_errors': workload.publisher_state.errors,
        'publish_resumed_after': workload.publisher_state.resumed_after(restore_time),
        'pull_resumed_after': workload.pull_state.resumed_after(restore_time),
        'push_resumed_after': workload.push_state.resumed_after(restore_time),
        'cleanup_resumed_after': workload.cleanup_state.resumed_after(restore_time),
    }

    return out

# ################################################################################################################################

def elapsed_since(start:'float') -> 'float':
    out = round(monotonic() - start, 3)
    return out

# ################################################################################################################################
# ################################################################################################################################
