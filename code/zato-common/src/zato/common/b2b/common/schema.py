# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, Index, Integer, MetaData, String, Table, UniqueConstraint

# Zato
from zato.common.db_env.common import Binary_Type, UTC_DateTime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class OpenKind:
    """ What an open record stands for - an exchange whose delivery has not ended, a business transaction
    that awaits a signal or a response, or a received message that the application has not confirmed yet.
    """
    Exchange    = 'exchange'
    Transaction = 'transaction'
    Delivery    = 'delivery'

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the identifier columns.
_short_column_len = 255

# The length of each column of the message identity. The unique key spans all four, and MySQL limits a key
# to 3072 bytes, which is 191 characters of utf8mb4 for each column.
_identity_column_len = 191

_identity_column = String(_identity_column_len)

# The length of an address column, which a unique key spans alone - 700 characters of utf8mb4 stay within
# the 3072 bytes of a MySQL key.
_address_column_len = 700

_address_column = String(_address_column_len)

# ################################################################################################################################
# ################################################################################################################################

metadata = MetaData()

# Row identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_sqlite_id_column_type = Integer()
_id_column_type = BigInteger().with_variant(_sqlite_id_column_type, 'sqlite')

_short_column = String(_short_column_len)
_time_column = UTC_DateTime()

# ################################################################################################################################

def _new_id_column() -> 'Column':
    """ Returns the autoincrement primary key of one table.
    """
    out = Column('id', _id_column_type, primary_key=True, autoincrement=True)
    return out

# ################################################################################################################################

message_table = Table('b2b_message', metadata,
    _new_id_column(),
    Column('protocol', _identity_column, nullable=False),
    Column('from_party', _identity_column, nullable=False),
    Column('to_party', _identity_column, nullable=False),
    Column('message_id', _identity_column, nullable=False),
    Column('status', _short_column, nullable=False),
    Column('received_at', _time_column, nullable=False),
    Column('expires_at', _time_column, nullable=False),
    Column('response_status_code', Integer, nullable=False),
    Column('response_content_type', _short_column, nullable=False),
    Column('response_body', Binary_Type, nullable=False),
    Column('response_is_synchronous', Boolean, nullable=False),

    # The transaction that claimed the row, on the databases whose claim statement returns no rows.
    Column('commit_id', _short_column, nullable=True),

    UniqueConstraint('protocol', 'from_party', 'to_party', 'message_id', name='uq_b2b_message_identity'),

    # Retention deletes on the expiry time, which without this index means reading the whole table on every run.
    Index('idx_b2b_message_expires', 'expires_at'),

    Index('idx_b2b_message_commit', 'commit_id'),
)

sequence_table = Table('b2b_sequence', metadata,
    Column('conversation', _short_column, primary_key=True),
    Column('next_sequence', BigInteger, nullable=False),
)

# A received message of an ordered conversation that waits for the messages before it. Its bytes are those
# of the audit event that recorded its receipt, which its delivery record points to once it is released.
# The retry window is how long the sender keeps sending the missing messages, and the time of the report
# is set on the earliest held message of a gap once the timeout of that gap is recorded.
held_message_table = Table('b2b_held_message', metadata,
    _new_id_column(),
    Column('conversation', _short_column, nullable=False),
    Column('sequence_number', BigInteger, nullable=False),
    Column('message_id', _short_column, nullable=False),
    Column('event_id', BigInteger, nullable=False),
    Column('held_at', _time_column, nullable=False),
    Column('retry_window_ms', BigInteger, nullable=False),
    Column('reported_at', _time_column, nullable=True),
    UniqueConstraint('conversation', 'sequence_number', name='uq_b2b_held_message'),
    Index('idx_b2b_held_message_time', 'held_at'),
    Index('idx_b2b_held_message_event', 'event_id'),

    # Retention keeps the events of a held message, which it finds by the MessageId of each event.
    Index('idx_b2b_held_message_id', 'message_id'),
)

# The delivery state of each address messages are sent to. An address with no row is active,
# and the consecutive failures are those of the transport, which a response of any other kind resets.
address_state_table = Table('b2b_address_state', metadata,
    _new_id_column(),
    Column('address', _address_column, nullable=False),
    Column('state', _short_column, nullable=False),
    Column('consecutive_failures', Integer, nullable=False),
    Column('changed_at', _time_column, nullable=False),
    Column('reason', _short_column, nullable=False),
    UniqueConstraint('address', name='uq_b2b_address_state'),
)

# One row for each exchange and each business transaction that has not ended, pointing at the audit event
# that started it. A server reads its own rows on start and nothing else, whatever the size of the audit log.
open_table = Table('b2b_open', metadata,
    _new_id_column(),
    Column('kind', _short_column, nullable=False),
    Column('source', _short_column, nullable=False),
    Column('server_name', _short_column, nullable=False),
    Column('message_id', _short_column, nullable=False),
    Column('event_id', BigInteger, nullable=False),
    Index('idx_b2b_open_server', 'source', 'server_name', 'kind'),
    Index('idx_b2b_open_message', 'message_id'),
)

# Prototype - the attributes of one B2B event as one row of columns, in place of one event_attr row per attribute.
b2b_event_attr_names = ('from_party', 'to_party', 'service', 'action', 'attempt', 'attempt_at', 'final_state',
    'signal_kind', 'error_code', 'deadline_at')

b2b_event_table = Table('b2b_event', metadata,
    Column('event_id', BigInteger, primary_key=True, autoincrement=False),
    *[Column(name, _short_column, nullable=True) for name in b2b_event_attr_names],
    Index('idx_b2b_event_parties', 'from_party', 'to_party'),
    Index('idx_b2b_event_operation', 'service', 'action'),
    Index('idx_b2b_event_final_state', 'final_state'),
)

from sqlalchemy import DDL, event as _sa_event
_search_expr = " || ' ' || ".join(f"coalesce({name}, '')" for name in ('from_party', 'to_party', 'service', 'action',
    'final_state', 'signal_kind', 'error_code'))
_sa_event.listen(b2b_event_table, 'after_create', DDL(
    f'CREATE INDEX idx_b2b_event_search ON b2b_event USING gin (({_search_expr}) gin_trgm_ops)').execute_if(
    dialect='postgresql'))

# ################################################################################################################################
# ################################################################################################################################

def create_tables(engine:'Engine') -> 'None':
    """ Creates the B2B tables in a database that does not have them yet.
    """
    metadata.create_all(engine)

# ################################################################################################################################
# ################################################################################################################################
