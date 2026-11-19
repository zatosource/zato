# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Seeding the pub/sub tables in bulk before a server starts - the backlogs of the subscriptions that the enmasse
# definition of the server creates, and the traces of delivered messages past their retention. The rows are generated
# as they are inserted, so that a seed of tens of millions of rows is never held in memory at once.

# stdlib
from datetime import datetime, timezone
from logging import getLogger
from time import monotonic
from typing import NamedTuple
from zlib import crc32

# Zato
from zato.common.common_db.schema import message_dedup_table
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.schema import active_table, delivery_table, message_table, metadata, topic_sub_table
from zato.common.test.direct_sql.reset import reset_table_rows, truncate_tables
from zato.common.test.direct_sql.seed import BulkLoad, ModuleCtx as SeedModuleCtx, refresh_statistics, seed_bulk
from zato.common.test.pubsub_database import get_db_mode, is_managed_mode
from zato.common.util.api import sub_key_from_definition
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, anytuple, strlist

    anytuplegen = Iterator[anytuple]
    tablelist   = list[Table]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many seeded messages each line of the progress of a seed stands for
    Progress_Every = 100_000

    # The publications of a backlog are spread backwards from the time of the seed by this many milliseconds each
    Pub_Time_Step_MS = 3540

    # How many seconds one year has and how many milliseconds one second and one day have
    Seconds_Per_Year = 365 * 24 * 60 * 60
    MS_Per_Second    = 1000
    MS_Per_Day       = 24 * 60 * 60 * 1000

    # The payload of each seeded message and its checksum
    Payload       = 'seed-payload-' + 'x' * 40
    Payload_CRC32 = crc32(Payload.encode('utf8'))

    # The priority of each seeded message, which is the default one
    Priority = 5

    # The prefix of the identifiers of the seeded messages
    Msg_ID_Prefix = 'zpsm.seed'

    # The statements that write the seeded pages to the database in a checkpoint of their own
    Checkpoint_PostgreSQL = 'checkpoint'
    Checkpoint_SQLite     = 'pragma wal_checkpoint(truncate)'

# ################################################################################################################################
# ################################################################################################################################

# The columns of pubsub_message in the order of the seeded rows, with the identifier given explicitly,
# so that the deliveries refer to their messages without a join.
_message_columns = ('id', 'msg_id', 'topic_name', 'payload', 'payload_encrypted', 'data_class', 'data_size',
    'data_preview', 'priority', 'expiration', 'pub_time_iso', 'recv_time_iso', 'expiration_time_iso', 'pub_time_ms',
    'expiration_ms', 'publisher', 'cid', 'correl_id', 'in_reply_to', 'ext_client_id', 'payload_crc32')

# The columns of pubsub_delivery, whose identifier the database assigns.
_delivery_columns = ('message_id', 'sub_key', 'topic_name', 'priority', 'expiration_ms')

# The columns of pubsub_topic_sub.
_sub_columns = ('sub_key', 'topic_name')

# ################################################################################################################################
# ################################################################################################################################

class SeededQueue(NamedTuple):
    """ The backlog of one subscription of the enmasse definition of a server - the security definition
    of its subscriber, its delivery type, its topic and how many messages are pending in it.
    """
    sec_name: 'str'
    delivery_type: 'str'
    topic_name: 'str'
    message_count: 'int'

seeded_queue_list = list[SeededQueue]

# ################################################################################################################################
# ################################################################################################################################

def _get_seeded_tables() -> 'tablelist':
    """ Every pub/sub table except the table of the generation, and the dedup records of the message IDs.
    """
    out:'tablelist' = [message_dedup_table]

    for table in reversed(metadata.sorted_tables):
        if table is not active_table:
            out.append(table)

    return out

# ################################################################################################################################

def _clear_tables(engine:'Engine') -> 'None':
    """ Empties the pub/sub tables, so that the identifiers of the seeded messages start at one. PostgreSQL truncates
    the tables and SQLite deletes their rows.
    """
    tables = _get_seeded_tables()

    if engine.dialect.name == Type_PostgreSQL:
        truncate_tables(engine, tables)
    else:
        reset_table_rows(engine, tables)

# ################################################################################################################################

def _write_checkpoint(engine:'Engine') -> 'None':
    """ Writes the seeded pages to the database in a checkpoint of its own, so that the checkpoint of the seed does not
    run during the measurement that follows it. A managed database runs its own checkpoints and its role holds
    no privilege to request one.
    """
    is_postgresql = engine.dialect.name == Type_PostgreSQL

    if is_postgresql and is_managed_mode(get_db_mode()):
        return

    if is_postgresql:
        statement = ModuleCtx.Checkpoint_PostgreSQL
    else:
        statement = ModuleCtx.Checkpoint_SQLite

    # A checkpoint writes no rows, and PostgreSQL runs it outside of a transaction only
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level=SeedModuleCtx.Autocommit)
        _ = connection.exec_driver_sql(statement)

# ################################################################################################################################

def _load(engine:'Engine', message_rows:'anytuplegen', delivery_rows:'anytuplegen', sub_rows:'anylist') -> 'None':
    """ Seeds the messages, their deliveries and the subscriptions in one transaction, refreshes the statistics
    of the tables, so that the planner sees the seeded rows at once, and writes the checkpoint.
    """
    loads = [
        BulkLoad(message_table, _message_columns, message_rows, True),
        BulkLoad(delivery_table, _delivery_columns, delivery_rows, False),
        BulkLoad(topic_sub_table, _sub_columns, iter(sub_rows), False),
    ]

    seed_bulk(engine, loads)

    tables = _get_seeded_tables()
    refresh_statistics(engine, tables)

    _write_checkpoint(engine)

# ################################################################################################################################

def _log_progress(kind:'str', seeded:'int', total:'int') -> 'None':
    """ Logs how many messages of a seed were generated for insertion, once per a given number of them.
    """
    if seeded % ModuleCtx.Progress_Every == 0:
        logger.info('Seed of %s -> %d of %d messages', kind, seeded, total)

# ################################################################################################################################

def _ms_to_iso(value_ms:'int') -> 'str':
    seconds = value_ms / ModuleCtx.MS_Per_Second
    value = datetime.fromtimestamp(seconds, tz=timezone.utc)

    out = value.isoformat()
    return out

# ################################################################################################################################

def get_seeded_sub_key(queue:'SeededQueue') -> 'str':
    """ Returns the subscription key that a server derives from the enmasse definition of the subscription of a queue.
    """
    out = sub_key_from_definition(queue.sec_name, queue.delivery_type, [queue.topic_name])
    return out

# ################################################################################################################################

def seed_queues(queues:'seeded_queue_list') -> 'float':
    """ Seeds the backlog of each queue - its messages, published over the time before the seed and expiring a year
    after it, each pending for the subscription of the queue. Starts from empty tables and returns how long
    the seed took, in seconds.
    """
    start = monotonic()

    engine = get_database_engine()
    _clear_tables(engine)

    now_ms = int(datetime_to_ms(utcnow()))
    now_iso = _ms_to_iso(now_ms)

    # The expiration is a year away, in milliseconds and in its ISO form alike ..
    expiration_ms = now_ms + ModuleCtx.Seconds_Per_Year * ModuleCtx.MS_Per_Second
    expiration_iso = _ms_to_iso(expiration_ms)

    sub_keys:'strlist' = []
    sub_rows:'anylist' = []

    for queue in queues:
        sub_key = get_seeded_sub_key(queue)
        sub_keys.append(sub_key)
        sub_rows.append((sub_key, queue.topic_name))

    # .. the messages of the queues follow one another, with identifiers counting up from one ..
    total = 0
    for queue in queues:
        total += queue.message_count

    def iter_messages() -> 'anytuplegen':
        message_id = 0

        for queue_index, queue in enumerate(queues):
            for number in range(queue.message_count):
                message_id += 1
                _log_progress('backlogs', message_id, total)
                msg_id = f'{ModuleCtx.Msg_ID_Prefix}.{queue_index:04d}.{number}'
                pub_time_ms = now_ms - number * ModuleCtx.Pub_Time_Step_MS

                yield (message_id, msg_id, queue.topic_name, ModuleCtx.Payload, False, None, len(ModuleCtx.Payload),
                    ModuleCtx.Payload, ModuleCtx.Priority, ModuleCtx.Seconds_Per_Year, now_iso, now_iso, expiration_iso,
                    pub_time_ms, expiration_ms, None, None, None, None, None, ModuleCtx.Payload_CRC32)

    # .. and each of them is pending for the subscription of its queue.
    def iter_deliveries() -> 'anytuplegen':
        message_id = 0

        for queue, sub_key in zip(queues, sub_keys):
            for _ in range(queue.message_count):
                message_id += 1
                yield (message_id, sub_key, queue.topic_name, ModuleCtx.Priority, expiration_ms)

    _load(engine, iter_messages(), iter_deliveries(), sub_rows)

    out = monotonic() - start
    return out

# ################################################################################################################################

def seed_traces(topic_name:'str', message_count:'int', age_days:'int') -> 'float':
    """ Seeds the traces of messages of one topic that were delivered to every subscriber the given number of days
    before the seed, without their payloads and without deliveries, which the retention of the cleanup removes.
    Starts from empty tables and returns how long the seed took, in seconds.
    """
    start = monotonic()

    engine = get_database_engine()
    _clear_tables(engine)

    now_ms = int(datetime_to_ms(utcnow()))

    # The traces were published long ago ..
    aged_ms = now_ms - age_days * ModuleCtx.MS_Per_Day
    aged_iso = _ms_to_iso(aged_ms)

    # .. and their expiration is still a year away.
    expiration_ms = now_ms + ModuleCtx.Seconds_Per_Year * ModuleCtx.MS_Per_Second
    expiration_iso = _ms_to_iso(expiration_ms)

    def iter_messages() -> 'anytuplegen':
        for number in range(message_count):
            message_id = number + 1
            _log_progress('traces', message_id, message_count)
            msg_id = f'{ModuleCtx.Msg_ID_Prefix}.trace.{number}'
            pub_time_ms = aged_ms - number

            yield (message_id, msg_id, topic_name, None, False, None, len(ModuleCtx.Payload), ModuleCtx.Payload,
                ModuleCtx.Priority, ModuleCtx.Seconds_Per_Year, aged_iso, aged_iso, expiration_iso, pub_time_ms,
                expiration_ms, None, None, None, None, None, ModuleCtx.Payload_CRC32)

    _load(engine, iter_messages(), iter([]), [])

    out = monotonic() - start
    return out

# ################################################################################################################################
# ################################################################################################################################
