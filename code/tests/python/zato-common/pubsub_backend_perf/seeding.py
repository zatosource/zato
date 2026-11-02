# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sqlite3
from datetime import datetime, timezone
from time import monotonic
from zlib import crc32

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.pubsub.sql.config import get_pubsub_db_path, get_pubsub_engine
from zato.common.pubsub.sql.schema import metadata
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, strlist

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

# The table of the generation, whose row the seeding keeps.
_active_table_name = 'pubsub_active'

# How the text format of COPY represents NULL.
_copy_null = '\\N'

# The columns of pubsub_message in seeding order - the id comes first and is assigned
# explicitly so delivery rows can reference messages without any join.
_message_columns = ('id, msg_id, topic_name, payload, payload_encrypted, data_class, data_size, data_preview,'
    ' priority, expiration, pub_time_iso, recv_time_iso, expiration_time_iso, pub_time_ms, expiration_ms,'
    ' publisher, cid, correl_id, in_reply_to, ext_client_id, payload_crc32')

# The columns of pubsub_delivery in seeding order - the id column is omitted
# because nothing references it, so the engine assigns it itself.
_delivery_columns = 'message_id, sub_key, topic_name, priority, expiration_ms'

# ################################################################################################################################
# ################################################################################################################################

def _is_postgresql() -> 'bool':
    engine = get_pubsub_engine()
    out = engine.dialect.name == Type_PostgreSQL
    return out

# ################################################################################################################################

def connect_native() -> 'anytuple':
    """ Opens a direct connection of the database driver for bulk seeding - SQLite's own module,
    or pg8000 for PostgreSQL. Returns the connection and the placeholder of the driver's parameters.
    """

    # The engine call makes sure the schema exists before the native connection uses it.
    engine = get_pubsub_engine()

    if engine.dialect.name == Type_PostgreSQL:
        connection = engine.raw_connection()
        out = (connection, '%s')
    else:
        db_path = get_pubsub_db_path()
        connection = sqlite3.connect(db_path)
        _ = connection.execute('pragma synchronous=off')
        out = (connection, '?')

    return out

# ################################################################################################################################

def _clear_all_tables(cursor:'any_') -> 'None':
    """ Empties all pub/sub tables by dropping them and creating them anew, together with the triggers
    of the count tables. SQLite deletes the rows of a table that has triggers one by one, which for
    the backlogs of the mass scenarios takes minutes, whereas dropping a table releases its pages at once.
    PostgreSQL truncates the tables instead, which keeps the objects the open connections refer to.
    """
    if _is_postgresql():
        table_names:'strlist' = []
        for table in metadata.sorted_tables:
            if table.name != _active_table_name:
                table_names.append(table.name)
        _ = cursor.execute(f'truncate table {", ".join(table_names)} restart identity')
        return

    for table in reversed(metadata.sorted_tables):
        _ = cursor.execute(f'drop table if exists {table.name}')

    engine = get_pubsub_engine()
    metadata.create_all(engine)

# ################################################################################################################################

def _copy_line(row:'anytuple') -> 'str':
    """ Turns one row into a line of the text format of COPY. The seeded values contain no tabs, newlines
    or backslashes, so only NULL needs a representation of its own.
    """
    values:'strlist' = []

    for value in row:
        if value is None:
            values.append(_copy_null)
        else:
            values.append(str(value))

    out = '\t'.join(values) + '\n'
    return out

# ################################################################################################################################

def _load_rows(cursor:'any_', table:'str', columns:'str', rows:'any_') -> 'None':
    """ Inserts rows through SQLite's executemany path or with COPY on PostgreSQL.
    """
    if _is_postgresql():
        lines = map(_copy_line, rows)
        _ = cursor.execute(f'copy {table} ({columns}) from stdin', stream=lines)
        return

    placeholder_count = columns.count(',') + 1
    placeholders = ', '.join(['?'] * placeholder_count)
    cursor.executemany(f'insert into {table} ({columns}) values ({placeholders})', rows)

# ################################################################################################################################

def _finish_load(cursor:'any_') -> 'None':
    """ On PostgreSQL, moves the sequence of the message keys past the keys that the seeding assigned itself,
    and updates the statistics of the tables, so that the planner sees the seeded rows at once.
    """
    if not _is_postgresql():
        return

    _ = cursor.execute(
        "select setval(pg_get_serial_sequence('pubsub_message', 'id'), (select max(id) from pubsub_message))")

    for table in metadata.sorted_tables:
        _ = cursor.execute(f'analyze {table.name}')

# ################################################################################################################################

def _write_checkpoint(connection:'any_') -> 'None':
    """ On PostgreSQL, writes the seeded pages to disk in a checkpoint of its own, so that the checkpoint
    of the seeding does not run over the scenario that follows it and slow its WAL flushes.
    """
    if not _is_postgresql():
        return

    cursor = connection.cursor()
    _ = cursor.execute('checkpoint')
    connection.commit()

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Empties all the pub/sub tables through the native driver.
    """
    connection, _ignored = connect_native()
    cursor = connection.cursor()

    _clear_all_tables(cursor)

    connection.commit()
    connection.close()

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

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch.
    _clear_all_tables(cursor)

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

                yield (message_id, msg_id, topic_name, _payload, 0, None, len(_payload), _payload,
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

    _load_rows(cursor, 'pubsub_message', _message_columns, iter_messages())
    _load_rows(cursor, 'pubsub_delivery', _delivery_columns, iter_deliveries())

    # The subscriptions themselves - a few thousand rows at most, executemany is enough.
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

    cursor.executemany(
        f'insert into pubsub_topic_sub (sub_key, topic_name) values ({placeholder}, {placeholder})', sub_rows)

    _finish_load(cursor)
    connection.commit()
    _write_checkpoint(connection)
    connection.close()

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

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch.
    _clear_all_tables(cursor)

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

            yield (message_id, msg_id, topic_name, payload, 0, None, len(_payload), _payload,
                _priority, _seconds_per_year, aged_iso, aged_iso, expiration_iso, pub_time_ms,
                expiration_ms, None, None, None, None, None, _payload_crc32)

    def iter_deliveries() -> 'any_':
        """ Only the laggards still hold every message pending.
        """
        for number in range(message_count):
            message_id = number + 1

            for sub_key in delivery_sub_keys:
                yield (message_id, sub_key, topic_name, _priority, expiration_ms)

    _load_rows(cursor, 'pubsub_message', _message_columns, iter_messages())
    _load_rows(cursor, 'pubsub_delivery', _delivery_columns, iter_deliveries())

    # Every peer stays subscribed for the traffic yet to come.
    sub_rows:'anylist' = []

    for sub_key in sub_keys:
        sub_rows.append((sub_key, topic_name))

    cursor.executemany(
        f'insert into pubsub_topic_sub (sub_key, topic_name) values ({placeholder}, {placeholder})', sub_rows)

    _finish_load(cursor)
    connection.commit()
    _write_checkpoint(connection)
    connection.close()

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
