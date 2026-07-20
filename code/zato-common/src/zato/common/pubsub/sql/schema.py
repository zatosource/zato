# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, Index, Integer, MetaData, String, Table, Text
from sqlalchemy.dialects.mysql import LONGTEXT

# Zato
from zato.common.api import PubSub

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

# ################################################################################################################################
# ################################################################################################################################

# Message identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_id_column_type = BigInteger().with_variant(Integer(), 'sqlite')

# MySQL's plain TEXT caps at 64 kB, so payloads need LONGTEXT there.
_payload_column_type = Text().with_variant(LONGTEXT(), 'mysql')

# ################################################################################################################################
# ################################################################################################################################

# All the pub/sub queue tables, portable across SQLite, MySQL, PostgreSQL and Oracle DB.
# Short columns are VARCHAR so MySQL can index them, and optional values are NULL,
# never '', because Oracle DB stores empty strings as NULLs.
metadata = MetaData()

# ################################################################################################################################

# One row per published message. The payload is set to NULL once every subscriber
# has acknowledged the message and the row stays behind as the delivered-message trace
# until the retention sweep removes it. The primary key is the publication sequence.
message_table = Table('pubsub_message', metadata,
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('msg_id', String(_short_column_len), nullable=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('payload', _payload_column_type, nullable=True),
    Column('payload_encrypted', Boolean, nullable=False),
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

    # Messages are looked up by their public identifier ..
    Index('idx_pubsub_message_msg_id', 'msg_id', unique=True),

    # .. browsing walks a topic in publication order ..
    Index('idx_pubsub_message_topic', 'topic_name', 'id'),

    # .. the publish timeline and publisher counts read a topic by publication time ..
    Index('idx_pubsub_message_topic_time', 'topic_name', 'pub_time_ms'),

    # .. and the expiry sweep finds everything that is past its time.
    Index('idx_pubsub_message_expiration', 'expiration_ms'),
)

# ################################################################################################################################

# One row per (message, subscriber) pair still awaiting acknowledgement. Rows are
# deleted on ack, so a message with no delivery rows left is fully delivered.
# Priority and expiration are denormalized from the message and there is no
# foreign key on purpose.
delivery_table = Table('pubsub_delivery', metadata,
    Column('id', _id_column_type, primary_key=True, autoincrement=True),
    Column('message_id', BigInteger, nullable=False),
    Column('sub_key', String(_short_column_len), nullable=False),
    Column('topic_name', String(_short_column_len), nullable=False),
    Column('priority', Integer, nullable=False),
    Column('expiration_ms', BigInteger, nullable=False),

    # Acknowledgements and last-subscriber checks look deliveries up by message ..
    Index('idx_pubsub_delivery_message', 'message_id'),

    # .. queue depths are counted per (subscriber, topic) pair ..
    Index('idx_pubsub_delivery_sub_topic', 'sub_key', 'topic_name'),

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

# One row per (subscriber, topic) subscription - the configuration-level
# subscription objects live in the ODB.
topic_sub_table = Table('pubsub_topic_sub', metadata,
    Column('sub_key', String(_short_column_len), primary_key=True),
    Column('topic_name', String(_short_column_len), primary_key=True),

    # Publishing needs all subscribers of one topic.
    Index('idx_pubsub_topic_sub_topic', 'topic_name'),
)

# ################################################################################################################################
# ################################################################################################################################
