# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Column, Index, MetaData, PrimaryKeyConstraint, String, Table
from sqlalchemy.dialects.postgresql import JSONB

# Zato
from zato.common.db_env.common import UTC_DateTime

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the type and the name of a shared object.
_name_column_len = 200

# Maximum length of the kind, the scope and the message ID of a dedup record.
_dedup_kind_len = 50
_dedup_scope_len = 200
_dedup_message_id_len = 200

# Maximum length of the fingerprint of the message of a dedup record.
_dedup_fingerprint_len = 400

# ################################################################################################################################
# ################################################################################################################################

# The tables of the shared objects in the Zato database.
metadata = MetaData()

# ################################################################################################################################

# One row per shared object - a JSON document under a type and a name, with the version that each write raises by one.
shared_object_table = Table('zato_shared_object', metadata,
    Column('object_type', String(_name_column_len), nullable=False),
    Column('name', String(_name_column_len), nullable=False),
    Column('data', JSONB(), nullable=False),
    Column('version', BigInteger, nullable=False),
    Column('last_updated', UTC_DateTime, nullable=False),
    PrimaryKeyConstraint('object_type', 'name'),
)

# ################################################################################################################################

# One dedup record per message ID received within its window - the kind of the messages, the scope within which
# their IDs are unique, the fingerprint of the content that the ID stands for, and when the record was written and expires,
# in milliseconds since the epoch. A record that expired is replaced by the next message with the same ID.
message_dedup_table = Table('zato_message_dedup', metadata,
    Column('kind', String(_dedup_kind_len), nullable=False),
    Column('scope', String(_dedup_scope_len), nullable=False),
    Column('message_id', String(_dedup_message_id_len), nullable=False),
    Column('fingerprint', String(_dedup_fingerprint_len), nullable=False),
    Column('received_ms', BigInteger, nullable=False),
    Column('expires_ms', BigInteger, nullable=False),
    PrimaryKeyConstraint('kind', 'scope', 'message_id'),
    Index('idx_zato_message_dedup_expires', 'expires_ms'),
)

# ################################################################################################################################
# ################################################################################################################################
