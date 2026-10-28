# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Boolean, Column, Index, Integer, LargeBinary, MetaData, String, Table, \
    UniqueConstraint

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class OpenKind:
    """ What an open record stands for - an exchange whose delivery has not ended,
    or a business transaction that awaits a signal or a response.
    """
    Exchange    = 'exchange'
    Transaction = 'transaction'

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of the identifier columns.
_short_column_len = 255

# The length of each column of the message identity. The unique key spans all four, and MySQL limits a key
# to 3072 bytes, which is 191 characters of utf8mb4 for each column.
_identity_column_len = 191

_identity_column = String(_identity_column_len)

# ################################################################################################################################
# ################################################################################################################################

metadata = MetaData()

# Row identifiers are 64-bit, except under SQLite where the autoincrement
# primary key must be a plain INTEGER to become an alias of the built-in rowid.
_sqlite_id_column_type = Integer()
_id_column_type = BigInteger().with_variant(_sqlite_id_column_type, 'sqlite')

_short_column = String(_short_column_len)

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
    Column('received_iso', _short_column, nullable=False),
    Column('expires_iso', _short_column, nullable=False),
    Column('response_status_code', Integer, nullable=False),
    Column('response_content_type', _short_column, nullable=False),
    Column('response_body', LargeBinary, nullable=False),
    Column('response_is_synchronous', Boolean, nullable=False),

    # The transaction that claimed the row, on the databases whose claim statement returns no rows.
    Column('commit_id', _short_column, nullable=True),

    UniqueConstraint('protocol', 'from_party', 'to_party', 'message_id', name='uq_b2b_message_identity'),

    # Retention deletes on the expiry time, which without this index means reading the whole table on every run.
    Index('idx_b2b_message_expires', 'expires_iso'),

    Index('idx_b2b_message_commit', 'commit_id'),
)

sequence_table = Table('b2b_sequence', metadata,
    Column('conversation', _short_column, primary_key=True),
    Column('next_sequence', BigInteger, nullable=False),
)

held_message_table = Table('b2b_held_message', metadata,
    _new_id_column(),
    Column('conversation', _short_column, nullable=False),
    Column('sequence_number', BigInteger, nullable=False),
    Column('content_type', _short_column, nullable=False),
    Column('body', LargeBinary, nullable=False),
    UniqueConstraint('conversation', 'sequence_number', name='uq_b2b_held_message'),
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

# ################################################################################################################################
# ################################################################################################################################

def create_tables(engine:'Engine') -> 'None':
    """ Creates the B2B tables in a database that does not have them yet.
    """
    metadata.create_all(engine)

# ################################################################################################################################
# ################################################################################################################################
