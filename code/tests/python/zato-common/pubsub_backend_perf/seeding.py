# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sqlite3
from datetime import datetime, timezone
from time import monotonic

# Zato
from zato.common.db_env import build_ssl_context_from_values, Type_MySQL, Type_SQLite
from zato.common.pubsub.sql.config import get_pubsub_engine, get_pubsub_env_values
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, strlist

# ################################################################################################################################
# ################################################################################################################################

# Default network ports when the environment does not name one
_mysql_default_port      = 3306
_postgresql_default_port = 5432

# Seeded messages are spread over the past hour so the publish timeline has data to bucket -
# with up to 1,000 messages per topic, a step of 3,540 ms covers 59 minutes
_pub_time_step_ms = 3540

# Seeded messages expire one year from now
_seconds_per_year = 365 * 24 * 60 * 60

# How many milliseconds one day has
_ms_per_day = 24 * 60 * 60 * 1000

# The payload every seeded message carries
_payload = 'seed-payload-' + 'x' * 40

# ################################################################################################################################
# ################################################################################################################################

def connect_native() -> 'anytuple':
    """ Opens a connection to the pub/sub database through its native driver,
    bypassing SQLAlchemy - bulk seeding needs the fastest path there is.
    Returns (connection, placeholder) with the driver's bind-parameter style.
    """

    # The engine call makes sure the schema exists before the native connection uses it
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

    # .. MySQL additionally needs || to mean string concatenation, as it does everywhere else ..
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
        )

        cursor = connection.cursor()
        _ = cursor.execute("set session sql_mode = concat(@@sql_mode, ',PIPES_AS_CONCAT')")
        cursor.close()

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

def delete_all_rows() -> 'None':
    """ Empties all the pub/sub tables through the native driver.
    """
    connection, _ignored = connect_native()
    cursor = connection.cursor()

    _ = cursor.execute('delete from pubsub_delivery')
    _ = cursor.execute('delete from pubsub_message')
    _ = cursor.execute('delete from pubsub_topic_sub')

    connection.commit()
    connection.close()

# ################################################################################################################################

def seed_backlog(
    *,
    topic_count:'int',
    messages_per_topic:'int',
    topic_prefix:'str' = 'perf.topic',
    sub_key_prefix:'str' = 'zpsk.perf',
    deep_sub_key:'str' = '',
    deep_topic_count:'int' = 0,
    ) -> 'float':
    """ Seeds a backlog of topic_count * messages_per_topic pending messages, one subscriber
    per topic, entirely inside the database - Python only writes topic_count base rows and
    the engine multiplies them with set-based INSERT ... SELECT statements, which is why
    a million messages plus their deliveries land in about two seconds.

    When deep_sub_key is given, it additionally subscribes that key to the first
    deep_topic_count topics, giving it deep_topic_count * messages_per_topic
    pending deliveries - the deep queue for clear-queue timing.

    Starts from empty tables. Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch ..
    _ = cursor.execute('delete from pubsub_delivery')
    _ = cursor.execute('delete from pubsub_message')
    _ = cursor.execute('delete from pubsub_topic_sub')

    # .. the multiplier table turns each base row into messages_per_topic rows -
    # .. the number is carried both as an integer for arithmetic and as text
    # .. for portable concatenation ..
    _ = cursor.execute('create temporary table seed_numbers (n_int integer, n_text varchar(10))')

    number_rows:'anylist' = []

    for number in range(messages_per_topic):
        number_rows.append((number, str(number)))

    cursor.executemany(f'insert into seed_numbers values ({placeholder}, {placeholder})', number_rows)

    # .. one base row per topic carries everything the multiplied rows share ..
    _ = cursor.execute("""create temporary table seed_base (
        msg_id varchar(200),
        topic_name varchar(200),
        sub_key varchar(200),
        payload varchar(200),
        data_size integer,
        pub_time_iso varchar(64),
        recv_time_iso varchar(64),
        expiration_time_iso varchar(64),
        pub_time_ms bigint,
        expiration_ms bigint)""")

    now = utcnow()
    now_iso = now.isoformat()
    now_ms = int(datetime_to_ms(now))
    expiration_ms = now_ms + _seconds_per_year * 1000

    base_rows:'anylist' = []

    for topic_index in range(topic_count):
        topic_name = f'{topic_prefix}.{topic_index:04d}'
        sub_key = f'{sub_key_prefix}.{topic_index:04d}'
        msg_id = f'zpsm.perf.{topic_index:04d}'

        base_rows.append((msg_id, topic_name, sub_key, _payload, len(_payload),
            now_iso, now_iso, now_iso, now_ms, expiration_ms))

    placeholders = ', '.join([placeholder] * 10)
    cursor.executemany(f'insert into seed_base values ({placeholders})', base_rows)

    # .. multiply the base rows into the full message backlog in one statement,
    # .. spreading publication times over the past hour for the timeline ..
    _ = cursor.execute("""
        insert into pubsub_message (msg_id, topic_name, payload, payload_encrypted, data_class,
            data_size, data_preview, priority, expiration, pub_time_iso, recv_time_iso,
            expiration_time_iso, pub_time_ms, expiration_ms, publisher, cid, correl_id,
            in_reply_to, ext_client_id)
        select
            b.msg_id || '.' || n.n_text, b.topic_name, b.payload, false, null,
            b.data_size, b.payload, 5, %d, b.pub_time_iso, b.recv_time_iso,
            b.expiration_time_iso, b.pub_time_ms - n.n_int * %d, b.expiration_ms, b.sub_key, null, null,
            null, null
        from seed_base b
        cross join seed_numbers n
    """ % (_seconds_per_year, _pub_time_step_ms))

    # .. every message is pending for its topic's subscriber ..
    _ = cursor.execute("""
        insert into pubsub_delivery (message_id, sub_key, topic_name, priority, expiration_ms)
        select m.id, b.sub_key, m.topic_name, m.priority, m.expiration_ms
        from pubsub_message m
        join seed_base b on b.topic_name = m.topic_name
    """)

    # .. record the subscriptions themselves ..
    _ = cursor.execute('insert into pubsub_topic_sub (sub_key, topic_name) select sub_key, topic_name from seed_base')

    # .. and give the deep subscriber its own pending copy of the first deep_topic_count topics.
    if deep_sub_key:

        deep_cutoff = f'{topic_prefix}.{deep_topic_count - 1:04d}'

        _ = cursor.execute(f"""
            insert into pubsub_delivery (message_id, sub_key, topic_name, priority, expiration_ms)
            select m.id, {placeholder}, m.topic_name, m.priority, m.expiration_ms
            from pubsub_message m
            where m.topic_name <= {placeholder}
        """, (deep_sub_key, deep_cutoff))

        _ = cursor.execute(f"""
            insert into pubsub_topic_sub (sub_key, topic_name)
            select {placeholder}, topic_name from seed_base where topic_name <= {placeholder}
        """, (deep_sub_key, deep_cutoff))

    _ = cursor.execute('drop table seed_numbers')
    _ = cursor.execute('drop table seed_base')

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
    have long acknowledged everything. Set-based, like seed_backlog.

    Starts from empty tables. Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    connection, placeholder = connect_native()
    cursor = connection.cursor()

    # Every run seeds from scratch ..
    _ = cursor.execute('delete from pubsub_delivery')
    _ = cursor.execute('delete from pubsub_message')
    _ = cursor.execute('delete from pubsub_topic_sub')

    # .. the multiplier table again carries its number both ways ..
    _ = cursor.execute('create temporary table seed_numbers (n_int integer, n_text varchar(10))')

    numbers_per_base = 1000

    number_rows:'anylist' = []

    for number in range(numbers_per_base):
        number_rows.append((number, str(number)))

    cursor.executemany(f'insert into seed_numbers values ({placeholder}, {placeholder})', number_rows)

    # .. the timestamps say these messages have been sitting here for months,
    # .. yet their expiration is still far away ..
    now = utcnow()
    now_ms = int(datetime_to_ms(now))

    aged_ms = now_ms - aged_days * _ms_per_day
    aged_iso = datetime.fromtimestamp(aged_ms / 1000, tz=timezone.utc).isoformat()
    expiration_ms = now_ms + _seconds_per_year * 1000

    # .. enough base rows that bases times numbers gives the requested count ..
    base_count = message_count // numbers_per_base

    _ = cursor.execute("""create temporary table seed_base (
        msg_id varchar(200),
        payload varchar(200),
        data_size integer,
        pub_time_iso varchar(64),
        pub_time_ms bigint,
        expiration_ms bigint)""")

    base_rows:'anylist' = []

    for base_index in range(base_count):
        msg_id = f'zpsm.aged.{base_index:04d}'
        base_rows.append((msg_id, _payload, len(_payload), aged_iso, aged_ms, expiration_ms))

    placeholders = ', '.join([placeholder] * 6)
    cursor.executemany(f'insert into seed_base values ({placeholders})', base_rows)

    # .. multiply the bases into the aged backlog ..
    _ = cursor.execute(f"""
        insert into pubsub_message (msg_id, topic_name, payload, payload_encrypted, data_class,
            data_size, data_preview, priority, expiration, pub_time_iso, recv_time_iso,
            expiration_time_iso, pub_time_ms, expiration_ms, publisher, cid, correl_id,
            in_reply_to, ext_client_id)
        select
            b.msg_id || '.' || n.n_text, {placeholder}, b.payload, false, null,
            b.data_size, b.payload, 5, {_seconds_per_year}, b.pub_time_iso, b.pub_time_iso,
            b.pub_time_iso, b.pub_time_ms - n.n_int, b.expiration_ms, null, null, null,
            null, null
        from seed_base b
        cross join seed_numbers n
    """, (topic_name,))

    # .. only the laggard still holds them all pending ..
    for sub_key in delivery_sub_keys:
        _ = cursor.execute(f"""
            insert into pubsub_delivery (message_id, sub_key, topic_name, priority, expiration_ms)
            select m.id, {placeholder}, m.topic_name, m.priority, m.expiration_ms
            from pubsub_message m
            where m.topic_name = {placeholder}
        """, (sub_key, topic_name))

    # .. while every peer stays subscribed for the traffic yet to come.
    for sub_key in sub_keys:
        _ = cursor.execute(
            f'insert into pubsub_topic_sub (sub_key, topic_name) values ({placeholder}, {placeholder})',
            (sub_key, topic_name))

    _ = cursor.execute('drop table seed_numbers')
    _ = cursor.execute('drop table seed_base')

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
