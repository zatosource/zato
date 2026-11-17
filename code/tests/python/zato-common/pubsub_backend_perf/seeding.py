# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
from datetime import datetime, timezone
from time import monotonic
from zlib import crc32

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.connection import set_sqlite_pragmas
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.pubsub.sql.schema import active_table, delivery_table, message_table, metadata, topic_sub_table
from zato.common.test.direct_sql.reset import recreate_tables, truncate_tables
from zato.common.test.direct_sql.seed import refresh_statistics, seed_bulk, BulkLoad
from zato.common.test.pubsub_database import get_db_mode, is_managed_mode
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Table
    from zato.common.typing_ import any_, anylist, anytuple, strlist

    tablelist = list[Table]

# ################################################################################################################################
# ################################################################################################################################

# Seeded messages are spread over the past hour so the publish timeline has data to bucket.
_pub_time_step_ms = 3540

# Seeded messages expire one year from now.
_seconds_per_year = 365 * 24 * 60 * 60

# How many milliseconds one day has.
_ms_per_day = 24 * 60 * 60 * 1000

# The payload every seeded message carries and its checksum.
_payload = 'seed-payload-' + 'x' * 40
_payload_crc32 = crc32(_payload.encode('utf8'))

# The priority every seeded message carries - the default one.
_priority = 5

# The columns of pubsub_message in seeding order - the id comes first and is assigned
# explicitly so delivery rows can reference messages without any join.
_message_columns = ('id', 'msg_id', 'topic_name', 'payload', 'payload_encrypted', 'data_class', 'data_size',
    'data_preview', 'priority', 'expiration', 'pub_time_iso', 'recv_time_iso', 'expiration_time_iso', 'pub_time_ms',
    'expiration_ms', 'publisher', 'cid', 'correl_id', 'in_reply_to', 'ext_client_id', 'payload_crc32')

# The columns of pubsub_delivery in seeding order - the id column is omitted
# because nothing references it, so the engine assigns it itself.
_delivery_columns = ('message_id', 'sub_key', 'topic_name', 'priority', 'expiration_ms')

# The columns of pubsub_topic_sub in seeding order.
_sub_columns = ('sub_key', 'topic_name')

# ################################################################################################################################
# ################################################################################################################################

def _is_postgresql() -> 'bool':
    engine = get_database_engine()
    out = engine.dialect.name == Type_PostgreSQL
    return out

# ################################################################################################################################

def connect_native() -> 'anytuple':
    """ Opens a direct connection of the database driver for bulk seeding - SQLite's own module,
    or pg8000 for PostgreSQL. Returns the connection and the placeholder of the driver's parameters.
    """

    # The engine call makes sure the schema exists before the native connection uses it.
    engine = get_database_engine()

    if engine.dialect.name == Type_PostgreSQL:
        connection = engine.raw_connection()
        out = (connection, '%s')
    else:
        db_path = os.environ[DatabaseEnv.Env_Path]
        connection = sqlite3.connect(db_path)
        set_sqlite_pragmas(connection, None)
        out = (connection, '?')

    return out

# ################################################################################################################################

def _get_seeded_tables() -> 'tablelist':
    """ Every pub/sub table except the table of the generation, whose row the seeding keeps.
    """
    out:'tablelist' = []

    for table in reversed(metadata.sorted_tables):
        if table is not active_table:
            out.append(table)

    return out

# ################################################################################################################################

def _clear_all_tables() -> 'None':
    """ Empties all pub/sub tables. SQLite deletes the rows of a table that has triggers one by one, which for
    the backlogs of the mass scenarios takes minutes, so the tables are dropped and created anew, together with
    the triggers of the count tables. PostgreSQL truncates the tables instead, which keeps the objects the open
    connections refer to.
    """
    engine = get_database_engine()

    if _is_postgresql():
        tables = _get_seeded_tables()
        truncate_tables(engine, tables)
    else:
        recreate_tables(engine, metadata)

# ################################################################################################################################

def _load(message_rows:'any_', delivery_rows:'any_', sub_rows:'anylist') -> 'None':
    """ Seeds the messages, their deliveries and the subscriptions in one transaction over the fastest path
    of the database and refreshes the statistics of the tables, so that the planner sees the seeded rows at once.
    """
    engine = get_database_engine()

    loads = [
        BulkLoad(message_table, _message_columns, message_rows, True),
        BulkLoad(delivery_table, _delivery_columns, delivery_rows, False),
        BulkLoad(topic_sub_table, _sub_columns, iter(sub_rows), False),
    ]

    seed_bulk(engine, loads)

    tables = _get_seeded_tables()
    refresh_statistics(engine, tables)

# ################################################################################################################################

def _write_checkpoint() -> 'None':
    """ Writes the seeded pages to the database in a checkpoint of its own, so that the checkpoint of the seeding
    does not run over the scenario that follows it and slow its WAL flushes. On SQLite, the checkpoint also truncates
    the WAL file of the seeding. A managed database runs its own checkpoints and its role holds no privilege to request one.
    """
    if _is_postgresql() and is_managed_mode(get_db_mode()):
        return

    connection, _ignored = connect_native()
    cursor = connection.cursor()

    if _is_postgresql():
        _ = cursor.execute('checkpoint')
    else:
        _ = cursor.execute('pragma wal_checkpoint(truncate)')

    connection.commit()
    connection.close()

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Empties all the pub/sub tables.
    """
    _clear_all_tables()

# ################################################################################################################################

def seed_backlog(
    *,
    topic_count:'int',
    messages_per_topic:'int',
    topic_prefix:'str' = 'perf.topic',
    sub_key_prefix:'str' = 'zpsk.perf',
    subscribers_per_topic:'int' = 1,
    deep_sub_key:'str' = '',
    deep_topic_count:'int' = 0,
    ) -> 'float':
    """ Seeds a backlog of topic_count * messages_per_topic pending messages.
    The rows are generated in Python and streamed into the database over each
    engine's bulk-load path - see _load_rows. Message ids are assigned explicitly,
    starting from 1 on freshly truncated tables, so the delivery rows reference
    their messages without any join.

    Each topic has subscribers_per_topic subscribers and each of them holds the topic's
    whole backlog pending. With one subscriber per topic its key is sub_key_prefix.NNNN,
    with more than one the keys are sub_key_prefix.NNNN.MMMM - the same naming
    the scenarios themselves use.

    When deep_sub_key is given, it additionally subscribes that key to the first
    deep_topic_count topics, giving it deep_topic_count * messages_per_topic
    pending deliveries - the deep queue for clear-queue timing.

    Starts from empty tables. Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    # Every run seeds from scratch.
    _clear_all_tables()

    now = utcnow()
    now_iso = now.isoformat()
    now_ms = int(datetime_to_ms(now))

    # The expiration is a year away and its ISO form must say the same thing -
    # push delivery reads the ISO form when it decides whether a message is stale.
    expiration_ms = now_ms + _seconds_per_year * 1000
    expiration_iso = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc).isoformat()

    def iter_messages() -> 'any_':
        """ One row per message, publication times spread over the past hour
        for the timeline, ids counting up from 1.
        """
        message_id = 0

        for topic_index in range(topic_count):
            topic_name = f'{topic_prefix}.{topic_index:04d}'
            sub_key = f'{sub_key_prefix}.{topic_index:04d}'

            for number in range(messages_per_topic):
                message_id += 1
                msg_id = f'zpsm.perf.{topic_index:04d}.{number}'
                pub_time_ms = now_ms - number * _pub_time_step_ms

                yield (message_id, msg_id, topic_name, _payload, False, None, len(_payload), _payload,
                    _priority, _seconds_per_year, now_iso, now_iso, expiration_iso, pub_time_ms,
                    expiration_ms, sub_key, None, None, None, None, _payload_crc32)

    def iter_deliveries() -> 'any_':
        """ One pending row per (message, subscriber) pair, walking the messages
        in the same order as iter_messages so the ids line up, plus the deep
        subscriber's own copy of the first deep_topic_count topics.
        """
        message_id = 0

        for topic_index in range(topic_count):
            topic_name = f'{topic_prefix}.{topic_index:04d}'
            sub_key = f'{sub_key_prefix}.{topic_index:04d}'

            for _number in range(messages_per_topic):
                message_id += 1

                if subscribers_per_topic == 1:
                    yield (message_id, sub_key, topic_name, _priority, expiration_ms)
                else:
                    for subscriber_index in range(subscribers_per_topic):
                        yield (message_id, f'{sub_key}.{subscriber_index:04d}', topic_name, _priority, expiration_ms)

                if deep_sub_key and topic_index < deep_topic_count:
                    yield (message_id, deep_sub_key, topic_name, _priority, expiration_ms)

    # The subscriptions themselves - a few thousand rows at most.
    sub_rows:'anylist' = []

    for topic_index in range(topic_count):
        topic_name = f'{topic_prefix}.{topic_index:04d}'
        sub_key = f'{sub_key_prefix}.{topic_index:04d}'

        if subscribers_per_topic == 1:
            sub_rows.append((sub_key, topic_name))
        else:
            for subscriber_index in range(subscribers_per_topic):
                sub_rows.append((f'{sub_key}.{subscriber_index:04d}', topic_name))

        if deep_sub_key and topic_index < deep_topic_count:
            sub_rows.append((deep_sub_key, topic_name))

    _load(iter_messages(), iter_deliveries(), sub_rows)
    _write_checkpoint()

    out = monotonic() - start
    return out

# ################################################################################################################################

def seed_aged_queue(
    *,
    topic_name:'str',
    sub_keys:'strlist',
    delivery_sub_keys:'strlist',
    message_count:'int',
    aged_days:'int',
    is_delivered:'bool' = False,
    ) -> 'float':
    """ Seeds one topic with message_count messages published aged_days in the past,
    pending only for delivery_sub_keys - the queue of a subscriber that has not
    acknowledged anything for months while its peers (the rest of sub_keys)
    have long acknowledged everything. Bulk-loaded, like seed_backlog.

    With is_delivered, the messages are delivered-message traces without their payloads,
    which the retention of the cleanup removes.

    Starts from empty tables. Returns the elapsed seeding time in seconds.
    """
    if is_delivered:
        payload = None
    else:
        payload = _payload

    start = monotonic()

    # Every run seeds from scratch.
    _clear_all_tables()

    # The timestamps say these messages have been sitting here for months,
    # yet their expiration is still far away ..
    now = utcnow()
    now_ms = int(datetime_to_ms(now))

    aged_ms = now_ms - aged_days * _ms_per_day
    aged_iso = datetime.fromtimestamp(aged_ms / 1000, tz=timezone.utc).isoformat()

    # .. the expiration is a year away and its ISO form must say the same thing -
    # .. push delivery reads the ISO form when it decides whether a message is stale.
    expiration_ms = now_ms + _seconds_per_year * 1000
    expiration_iso = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc).isoformat()

    def iter_messages() -> 'any_':
        """ One row per aged message, ids counting up from 1, each published
        a millisecond earlier than the previous one.
        """
        for number in range(message_count):
            message_id = number + 1
            msg_id = f'zpsm.aged.{number}'
            pub_time_ms = aged_ms - number

            yield (message_id, msg_id, topic_name, payload, False, None, len(_payload), _payload,
                _priority, _seconds_per_year, aged_iso, aged_iso, expiration_iso, pub_time_ms,
                expiration_ms, None, None, None, None, None, _payload_crc32)

    def iter_deliveries() -> 'any_':
        """ Only the laggards still hold every message pending.
        """
        for number in range(message_count):
            message_id = number + 1

            for sub_key in delivery_sub_keys:
                yield (message_id, sub_key, topic_name, _priority, expiration_ms)

    # Every peer stays subscribed for the traffic yet to come.
    sub_rows:'anylist' = []

    for sub_key in sub_keys:
        sub_rows.append((sub_key, topic_name))

    _load(iter_messages(), iter_deliveries(), sub_rows)
    _write_checkpoint()

    out = monotonic() - start
    return out

# ################################################################################################################################

def count_payloads(topic_name:'str') -> 'int':
    """ Counts the messages of one topic whose payload is still retained, i.e. not yet
    dropped by full delivery.
    """
    connection, placeholder = connect_native()
    cursor = connection.cursor()

    _ = cursor.execute(
        f'select count(*) from pubsub_message where topic_name = {placeholder} and payload is not null',
        (topic_name,))
    row:'any_' = cursor.fetchone()

    connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def count_rows(table_name:'str') -> 'int':
    """ Counts the rows of one table through the native driver.
    """
    connection, _ignored = connect_native()
    cursor = connection.cursor()

    _ = cursor.execute(f'select count(*) from {table_name}')
    row:'any_' = cursor.fetchone()

    connection.close()

    out = row[0]
    return out

# ################################################################################################################################
# ################################################################################################################################
