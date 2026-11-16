# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, DDL, event, Identity, Index, Integer, MetaData, PrimaryKeyConstraint, \
    String, Table, Text

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.pubsub.sql.counts import register_counts
from zato.common.pubsub.sql.traces import register_traces

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding all pub/sub messages and queue state.
pubsub_db_file_name = 'pubsub.db'

# Maximum length of short string columns - names, keys and identifiers.
_short_column_len = 200

# Maximum length of ISO-8601 timestamp columns.
_timestamp_column_len = 64

# Maximum length of the column holding fully-qualified Python class names.
_data_class_column_len = 400

# How long the stored preview of each payload is.
_data_preview_len = PubSub.Message.Data_Preview_Len

_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

# SQLite requires INTEGER for an autoincrementing primary key to alias its built-in rowid,
# which is 64-bit there, while PostgreSQL needs BIGINT for the same range.
_id_type = BigInteger().with_variant(Integer(), Type_SQLite)

def _new_id_column() -> 'Column':
    out = Column('id', _id_type, Identity(), primary_key=True)
    return out

# ################################################################################################################################

def _key(*names:'str') -> 'PrimaryKeyConstraint':
    """ The key of a count table. SQLite keeps one row per key, which is the primary key of its count tables,
    while PostgreSQL inserts many change rows per key, so the key is a plain index there - see counts.py.
    """
    out = PrimaryKeyConstraint(*names)
    out = out.ddl_if(dialect=Type_SQLite)

    return out

# ################################################################################################################################

def _key_index(name:'str', *names:'str') -> 'Index':
    """ The index by which PostgreSQL reads and compacts the change rows of one key of a count table.
    """
    out = Index(name, *names)
    out = out.ddl_if(dialect=Type_PostgreSQL)

    return out

# ################################################################################################################################
# ################################################################################################################################

# All pub/sub queue tables in the SQLite store.
metadata = MetaData()

# ################################################################################################################################

# One row per published message. The payload is set to NULL once every subscriber
# has acknowledged the message and the row stays behind as the delivered-message trace
# until the retention sweep removes it, listed in pubsub_trace. The primary key is the publication sequence.
message_table = Table('pubsub_message', metadata,
    _new_id_column(),
    Column('msg_id', String(_short_column_len), nullable=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('payload', Text, nullable=True),
    Column('payload_encrypted', Boolean, nullable=False),

    # The CRC-32 of the payload as published, before any encryption, by which a publication repeated
    # with the same identifier is told apart from a different message reusing the identifier
    Column('payload_crc32', BigInteger, nullable=False),

    Column('data_class', String(_data_class_column_len), nullable=True),
    Column('data_size', Integer, nullable=False),
    Column('data_preview', String(_data_preview_len), nullable=True),
    Column('priority', Integer, nullable=False),
    Column('expiration', Integer, nullable=False),
    Column('pub_time_iso', String(_timestamp_column_len), nullable=False),
    Column('recv_time_iso', String(_timestamp_column_len), nullable=False),
    Column('expiration_time_iso', String(_timestamp_column_len), nullable=False),
    Column('pub_time_ms', BigInteger, nullable=False),
    Column('expiration_ms', BigInteger, nullable=False),
    Column('publisher', String(_short_column_len), nullable=True),
    Column('cid', String(_short_column_len), nullable=True),
    Column('correl_id', String(_short_column_len), nullable=True),
    Column('in_reply_to', String(_short_column_len), nullable=True),
    Column('ext_client_id', String(_short_column_len), nullable=True),

    # The retry settings the publisher gave, if any
    Column(_retry.Field_Max_Retries, Integer, nullable=True),
    Column(_retry.Field_Sleep_Time, Integer, nullable=True),
    Column(_retry.Field_Backoff_Threshold, Integer, nullable=True),
    Column(_retry.Field_Backoff_Multiplier, Integer, nullable=True),

    # Messages are looked up by their public identifier ..
    Index('idx_pubsub_message_msg_id', 'msg_id', unique=True),

    # .. browsing walks a topic in publication order ..
    Index('idx_pubsub_message_topic', 'topic_name', 'id'),

    # .. and the expiry sweep finds everything that is past its time.
    Index('idx_pubsub_message_expiration', 'expiration_ms'),
)

# The retry columns, for the queries that read a message back
message_retry_columns = []

for _name in _retry.FieldList:
    message_retry_columns.append(message_table.c[_name])

# ################################################################################################################################

# One row per (message, subscriber) pair still awaiting acknowledgement. Rows are
# deleted on ack, so a message with no delivery rows left is fully delivered.
# Priority and expiration are denormalized from the message and there is no
# foreign key on purpose.
delivery_table = Table('pubsub_delivery', metadata,
    _new_id_column(),
    Column('message_id', BigInteger, nullable=False),
    Column('sub_key', String(_short_column_len), nullable=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('priority', Integer, nullable=False),
    Column('expiration_ms', BigInteger, nullable=False),

    # How many push attempts were made for this row, each one recorded before its HTTP request is sent,
    # or how many times a pull handed it out
    Column('attempt', Integer, nullable=False, server_default='0'),

    # Until when the row belongs to the pull that handed it out, in milliseconds since the epoch - the subscriber
    # acknowledges it before then, or the next pull after then hands it out again, and zero means it was not handed out.
    Column('leased_until_ms', BigInteger, nullable=False, server_default='0'),

    # Acknowledgements and last-subscriber checks look deliveries up by message ..
    Index('idx_pubsub_delivery_message', 'message_id'),

    # .. the pending messages of one (subscriber, topic) pair are browsed in publication order ..
    Index('idx_pubsub_delivery_sub_topic_message', 'sub_key', 'topic_name', 'message_id'),

    # .. and topic-wide operations walk all deliveries of one topic.
    Index('idx_pubsub_delivery_topic', 'topic_name'),
)

# The index behind the fetch query, declared outside the table
# because only column objects can express DESC ordering.
_ = Index(
    'idx_pubsub_delivery_fetch',
    delivery_table.c.sub_key,
    delivery_table.c.priority.desc(),
    delivery_table.c.message_id,
)

# ################################################################################################################################

# One row per delivered-message trace, which triggers of the database insert and delete along with
# the message rows - see traces.py.
trace_table = Table('pubsub_trace', metadata,
    Column('message_id', _id_type, primary_key=True, autoincrement=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('pub_time_ms', BigInteger, nullable=False),

    # The cap sweep walks the traces of one topic in publication order ..
    Index('idx_pubsub_trace_topic', 'topic_name', 'message_id'),

    # .. and the retention sweep finds the oldest ones.
    Index('idx_pubsub_trace_pub_time', 'pub_time_ms'),
)

# ################################################################################################################################

# One row per (subscriber, topic) subscription - the configuration-level
# subscription objects live in the ODB.
topic_sub_table = Table('pubsub_topic_sub', metadata,
    Column('sub_key', String(_short_column_len), primary_key=True),
    Column('topic_name', String(_short_column_len), primary_key=True),

    # Publishing needs all subscribers of one topic.
    Index('idx_pubsub_topic_sub_topic', 'topic_name'),
)

# ################################################################################################################################

# The number of delivery rows of each (subscriber, topic) pair.
queue_count_table = Table('pubsub_queue_count', metadata,
    Column('sub_key', String(_short_column_len), nullable=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('depth', BigInteger, nullable=False),
    _key('sub_key', 'topic_name'),
    _key_index('idx_pubsub_queue_count_key', 'sub_key', 'topic_name'),
    sqlite_with_rowid=False,
)

# The number of message rows of each topic, delivered traces included.
topic_count_table = Table('pubsub_topic_count', metadata,
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('total', BigInteger, nullable=False),
    _key('topic_name'),
    _key_index('idx_pubsub_topic_count_key', 'topic_name'),
    sqlite_with_rowid=False,
)

# The number of the message rows of each topic, minute of publication and publisher.
# Messages published without a publisher are counted under No_Publisher.
publish_count_table = Table('pubsub_publish_count', metadata,
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('minute_ms', BigInteger, nullable=False, autoincrement=False),
    Column('publisher', String(_short_column_len), nullable=False),
    Column('total', BigInteger, nullable=False),
    _key('topic_name', 'minute_ms', 'publisher'),
    _key_index('idx_pubsub_publish_count_key', 'topic_name', 'minute_ms', 'publisher'),
    sqlite_with_rowid=False,
)

# The triggers that keep the counts and the traces in step with the rows are created along with the tables.
register_counts(metadata)
register_traces(metadata)

# ################################################################################################################################

# The single row with the generation of the active server and the value unique to that server. Each server that starts
# on PostgreSQL raises the generation and writes its own value, and every pub/sub transaction confirms that both
# are still those of its server - see generation.py.
active_table = Table('pubsub_active', metadata,
    Column('id', Integer, primary_key=True, autoincrement=False),
    Column('generation', BigInteger, nullable=False),
    Column('owner', String(_short_column_len), nullable=False, server_default=''),
)

# The row exists from the moment the table does.
event.listen(active_table, 'after_create', DDL('INSERT INTO pubsub_active (id, generation) VALUES (1, 0)'))

# A PostgreSQL database created before the owner column receives it when the schema is next created. The column
# is looked up first, so that a database that has it takes no lock on the table, which the transactions
# of a previous server may hold.
_add_owner_column = DDL(f'''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = 'pubsub_active' AND column_name = 'owner'
    ) THEN
        ALTER TABLE pubsub_active ADD COLUMN owner VARCHAR({_short_column_len}) NOT NULL DEFAULT '';
    END IF;
END
$$
''')

_add_owner_column = _add_owner_column.execute_if(dialect=Type_PostgreSQL)
event.listen(metadata, 'after_create', _add_owner_column)

# ################################################################################################################################

# The storage of the tables on PostgreSQL. A message row keeps free space in its page, so that dropping its payload
# on acknowledgement and recording a delivery attempt are updates within the page that touch no index.
# Rows of every table are inserted and deleted at the rate of the traffic, so autovacuum runs after a small fraction
# of each table changed rather than the default fifth of it.
_high_churn = 'autovacuum_vacuum_scale_factor = 0.01, autovacuum_vacuum_insert_scale_factor = 0.01, ' + \
    'autovacuum_analyze_scale_factor = 0.02'

_toast_high_churn = 'toast.autovacuum_vacuum_scale_factor = 0.01, toast.autovacuum_vacuum_insert_scale_factor = 0.01'

_postgresql_storage = {
    message_table: [
        'ALTER TABLE pubsub_message ALTER COLUMN payload SET COMPRESSION lz4',
        f'ALTER TABLE pubsub_message SET (fillfactor = 90, {_high_churn}, {_toast_high_churn})',
    ],
    delivery_table: [
        f'ALTER TABLE pubsub_delivery SET (fillfactor = 90, {_high_churn})',
    ],
    trace_table: [
        f'ALTER TABLE pubsub_trace SET ({_high_churn})',
    ],
    queue_count_table: [
        f'ALTER TABLE pubsub_queue_count SET ({_high_churn})',
    ],
    topic_count_table: [
        f'ALTER TABLE pubsub_topic_count SET ({_high_churn})',
    ],
    publish_count_table: [
        f'ALTER TABLE pubsub_publish_count SET ({_high_churn})',
    ],
}

for _table, _statements in _postgresql_storage.items():
    for _statement in _statements:
        _ddl = DDL(_statement)
        _ddl = _ddl.execute_if(dialect=Type_PostgreSQL)
        event.listen(_table, 'after_create', _ddl)

# ################################################################################################################################
# ################################################################################################################################
