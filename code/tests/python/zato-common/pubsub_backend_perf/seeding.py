# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
from datetime import datetime, timezone
from tempfile import gettempdir
from time import monotonic

# Zato
from zato.common.db_env import build_ssl_context_from_values, Type_MySQL, Type_PostgreSQL, Type_SQLite
from zato.common.pubsub.sql.config import get_pubsub_engine, get_pubsub_env_values
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, strlist

# ################################################################################################################################
# ################################################################################################################################

# Default network ports when the environment does not name one.
_mysql_default_port      = 3306
_postgresql_default_port = 5432

# Seeded messages are spread over the past hour so the publish timeline has data to bucket.
_pub_time_step_ms = 3540

# Seeded messages expire one year from now.
_seconds_per_year = 365 * 24 * 60 * 60

# How many milliseconds one day has.
_ms_per_day = 24 * 60 * 60 * 1000

# The payload every seeded message carries.
_payload = 'seed-payload-' + 'x' * 40

# The priority every seeded message carries - the default one.
_priority = 5

# The NULL marker both LOAD DATA INFILE and COPY understand in CSV data.
_csv_null = '\\N'

# The columns of pubsub_message in seeding order - the id comes first and is assigned
# explicitly so delivery rows can reference messages without any join.
_message_columns = ('id, msg_id, topic_name, payload, payload_encrypted, data_class, data_size, data_preview,'
    ' priority, expiration, pub_time_iso, recv_time_iso, expiration_time_iso, pub_time_ms, expiration_ms,'
    ' publisher, cid, correl_id, in_reply_to, ext_client_id')

# The columns of pubsub_delivery in seeding order - the id column is omitted
# because nothing references it, so the engine assigns it itself.
_delivery_columns = 'message_id, sub_key, topic_name, priority, expiration_ms'

# ################################################################################################################################
# ################################################################################################################################

def connect_native() -> 'anytuple':
    """ Opens a connection to the pub/sub database through its native driver,
    bypassing SQLAlchemy - bulk seeding needs the fastest path there is.
    Returns (connection, placeholder) with the driver's bind-parameter style.
    """

    # The engine call makes sure the schema exists before the native connection uses it.
    _ = get_pubsub_engine()

    values = get_pubsub_env_values()
    db_type = values['type']

    # SQLite is a direct file connection with durability off - seed data is throwaway ..
    if db_type == Type_SQLite:
        connection = sqlite3.connect(values['name'])
        _ = connection.execute('pragma synchronous=off')

        out = (connection, '?')
        return out

    # .. the network databases reuse the same SSL context the engine itself would build ..
    if values['ssl']:
        ssl_context = build_ssl_context_from_values(values)
    else:
        ssl_context = None

    if port := values['port']:
        port = int(port)

    # .. MySQL additionally allows LOAD DATA LOCAL INFILE, the bulk-seeding path ..
    if db_type == Type_MySQL:
        import pymysql

        if not port:
            port = _mysql_default_port

        connection = pymysql.connect(
            host=values['host'],
            port=port,
            user=values['username'],
            password=values['password'],
            database=values['name'],
            ssl=ssl_context,
            local_infile=True,
        )

    # .. and PostgreSQL takes the context under its own keyword.
    else:
        import pg8000

        if not port:
            port = _postgresql_default_port

        connection = pg8000.connect(
            user=values['username'],
            password=values['password'],
            host=values['host'],
            port=port,
            database=values['name'],
            ssl=ssl_context,
        )

    out = (connection, '%s')
    return out

# ################################################################################################################################

def _clear_all_tables(cursor:'any_', db_type:'str') -> 'None':
    """ Empties all the pub/sub tables. The network databases use TRUNCATE because
    it is instant regardless of the row count, while a million-row DELETE takes
    minutes and generates an equally large undo log. TRUNCATE also resets the
    autoincrement counters, which the explicit message ids of bulk seeding rely on.
    SQLite keeps DELETE - it has no TRUNCATE and its DELETE without a WHERE clause
    is already the fast truncate-optimization path.
    """
    if db_type == Type_SQLite:
        _ = cursor.execute('delete from pubsub_delivery')
        _ = cursor.execute('delete from pubsub_message')
        _ = cursor.execute('delete from pubsub_topic_sub')

    elif db_type == Type_MySQL:
        _ = cursor.execute('truncate table pubsub_delivery')
        _ = cursor.execute('truncate table pubsub_message')
        _ = cursor.execute('truncate table pubsub_topic_sub')

    else:
        _ = cursor.execute('truncate table pubsub_delivery, pubsub_message, pubsub_topic_sub restart identity')

# ################################################################################################################################

def _write_csv(csv_path:'str', rows:'any_') -> 'None':
    """ Writes the rows out as CSV - the values are numbers and strings that never
    contain commas, quotes or newlines, so plain joining is all the encoding needed.
    None becomes the \\N marker both engines recognize as NULL.
    """
    with open(csv_path, 'w') as csv_file:
        for row in rows:
            items:'anylist' = []
            for value in row:
                if value is None:
                    items.append(_csv_null)
                else:
                    items.append(str(value))
            _ = csv_file.write(','.join(items) + '\n')

# ################################################################################################################################

def _load_rows(cursor:'any_', db_type:'str', table:'str', columns:'str', rows:'any_') -> 'None':
    """ Streams the rows into the table over the fastest path each engine has.
    SQLite is in-process, so executemany straight off the row generator is that path.
    The network databases get the rows as a CSV file fed to their bulk-load statements -
    LOAD DATA LOCAL INFILE and COPY FROM STDIN - which are engine-side loaders,
    an order of magnitude faster than any INSERT the wire protocol can carry.
    The CSV file is deleted as soon as the load is done.
    """
    if db_type == Type_SQLite:
        placeholders = ', '.join(['?'] * (columns.count(',') + 1))
        cursor.executemany(f'insert into {table} ({columns}) values ({placeholders})', rows)
        return

    csv_path = os.path.join(gettempdir(), f'zato-seed-{os.getpid()}-{table}.csv')
    _write_csv(csv_path, rows)

    if db_type == Type_MySQL:
        _ = cursor.execute(f"""
            load data local infile '{csv_path}'
            into table {table}
            fields terminated by ','
            lines terminated by '\\n'
            ({columns})
        """)
    else:
        with open(csv_path, 'rb') as csv_file:
            _ = cursor.execute(f"copy {table} ({columns}) from stdin with (format csv, null '{_csv_null}')", stream=csv_file)

    os.remove(csv_path)

# ################################################################################################################################

def _fix_message_sequence(cursor:'any_', db_type:'str', max_message_id:'int') -> 'None':
    """ Moves the id counter of pubsub_message past the explicitly assigned seed ids.
    Only PostgreSQL needs this - COPY does not touch the sequence, so the next regular
    publish would collide with a seeded id. MySQL and SQLite move their counters
    to max(id) + 1 on their own whenever explicit values are inserted.
    """
    if db_type == Type_PostgreSQL:
        _ = cursor.execute(f"select setval(pg_get_serial_sequence('pubsub_message', 'id'), {max_message_id})")

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Empties all the pub/sub tables through the native driver.
    """
    values = get_pubsub_env_values()

    connection, _ignored = connect_native()
    cursor = connection.cursor()

    _clear_all_tables(cursor, values['type'])

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

    values = get_pubsub_env_values()
    db_type = values['type']

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch.
    _clear_all_tables(cursor, db_type)

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
                    expiration_ms, sub_key, None, None, None, None)

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

    _load_rows(cursor, db_type, 'pubsub_message', _message_columns, iter_messages())
    _load_rows(cursor, db_type, 'pubsub_delivery', _delivery_columns, iter_deliveries())

    _fix_message_sequence(cursor, db_type, topic_count * messages_per_topic)

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

    connection.commit()
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
    ) -> 'float':
    """ Seeds one topic with message_count messages published aged_days in the past,
    pending only for delivery_sub_keys - the queue of a subscriber that has not
    acknowledged anything for months while its peers (the rest of sub_keys)
    have long acknowledged everything. Bulk-loaded, like seed_backlog.

    Starts from empty tables. Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    values = get_pubsub_env_values()
    db_type = values['type']

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch.
    _clear_all_tables(cursor, db_type)

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

            yield (message_id, msg_id, topic_name, _payload, 0, None, len(_payload), _payload,
                _priority, _seconds_per_year, aged_iso, aged_iso, expiration_iso, pub_time_ms,
                expiration_ms, None, None, None, None, None)

    def iter_deliveries() -> 'any_':
        """ Only the laggards still hold every message pending.
        """
        for number in range(message_count):
            message_id = number + 1

            for sub_key in delivery_sub_keys:
                yield (message_id, sub_key, topic_name, _priority, expiration_ms)

    _load_rows(cursor, db_type, 'pubsub_message', _message_columns, iter_messages())
    _load_rows(cursor, db_type, 'pubsub_delivery', _delivery_columns, iter_deliveries())

    _fix_message_sequence(cursor, db_type, message_count)

    # Every peer stays subscribed for the traffic yet to come.
    sub_rows:'anylist' = []

    for sub_key in sub_keys:
        sub_rows.append((sub_key, topic_name))

    cursor.executemany(
        f'insert into pubsub_topic_sub (sub_key, topic_name) values ({placeholder}, {placeholder})', sub_rows)

    connection.commit()
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
