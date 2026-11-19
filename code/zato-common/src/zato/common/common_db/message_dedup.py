# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The dedup records of message IDs, shared by every kind of messages whose IDs are recognized as repeats within a window.
# A dedup record is written by an upsert that replaces only a dedup record that expired, so an ID whose dedup record
# remains is a repeat, or a different message under the same ID, whichever its fingerprint says.

# stdlib
import time

# SQLAlchemy
from sqlalchemy import and_, bindparam, select, tuple_
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Zato
from zato.common.common_db.schema import message_dedup_table
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.db_env.plain_sql import PlainStatement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, anylist, callable_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class Kind:
    """ The kinds of messages whose IDs have dedup records.
    """
    Pubsub = 'pubsub'

# ################################################################################################################################
# ################################################################################################################################

_columns = message_dedup_table.c

# The columns that identify one dedup record.
_key_columns = (_columns.kind, _columns.scope, _columns.message_id)

# ################################################################################################################################
# ################################################################################################################################

def new_dedup_upsert(dialect_name:'str') -> 'any_':
    """ Returns the upsert of dedup records for a dialect. A dedup record that exists is replaced only if it expired
    by the time the new one was received, and the statement returns the message IDs of the dedup records it wrote.
    """
    if dialect_name == Type_PostgreSQL:
        out = postgresql_insert(message_dedup_table)
    else:
        out = sqlite_insert(message_dedup_table)

    excluded = out.excluded

    out = out.on_conflict_do_update(
        index_elements=_key_columns,
        set_={
            _columns.fingerprint.name: excluded.fingerprint,
            _columns.received_ms.name: excluded.received_ms,
            _columns.expires_ms.name: excluded.expires_ms,
        },
        where=_columns.expires_ms <= excluded.received_ms,
    )
    out = out.returning(_columns.message_id)

    return out

# ################################################################################################################################

# The upsert of the dedup records of a commit, for each dialect, executed as plain SQL.
dedup_upserts:'anydict' = {
    Type_SQLite: PlainStatement(new_dedup_upsert(Type_SQLite)),
    Type_PostgreSQL: PlainStatement(new_dedup_upsert(Type_PostgreSQL)),
}

# ################################################################################################################################

# The fingerprint of each given message ID of one kind and scope, and when its dedup record expires.
_dedup_records_query = select(_columns.message_id, _columns.fingerprint, _columns.expires_ms)
_dedup_records_query = _dedup_records_query.where(and_(
    _columns.kind == bindparam('dedup_kind'),
    _columns.scope == bindparam('dedup_scope'),
    _columns.message_id.in_(bindparam('dedup_message_ids', expanding=True)),
))
dedup_records_query = PlainStatement(_dedup_records_query)

# The fingerprint of one message ID of one kind and scope, and when its dedup record expires.
dedup_record_query = select(_columns.fingerprint, _columns.expires_ms)
dedup_record_query = dedup_record_query.where(and_(
    _columns.kind == bindparam('dedup_kind'),
    _columns.scope == bindparam('dedup_scope'),
    _columns.message_id == bindparam('dedup_message_id'),
))

# ################################################################################################################################

# The next batch of the dedup records that expired. The records are locked on PostgreSQL,
# and those that other transactions hold are skipped.
_expired_query = select(*_key_columns)
_expired_query = _expired_query.where(_columns.expires_ms <= bindparam('now_ms'))
_expired_query = _expired_query.limit(bindparam('batch_size'))
_expired_query = _expired_query.with_for_update(skip_locked=True)

# ################################################################################################################################
# ################################################################################################################################

def new_dedup_record(kind:'str', scope:'str', message_id:'str', fingerprint:'str', received_ms:'int', expires_ms:'int') -> 'anydict':
    """ Returns the row of one dedup record.
    """
    out = {
        _columns.kind.name: kind,
        _columns.scope.name: scope,
        _columns.message_id.name: message_id,
        _columns.fingerprint.name: fingerprint,
        _columns.received_ms.name: received_ms,
        _columns.expires_ms.name: expires_ms,
    }

    return out

# ################################################################################################################################

def sweep_expired(engine:'Engine', now_ms:'int', batch_size:'int', pause_after_batch:'callable_') -> 'int':
    """ Deletes the dedup records that expired by the given time, in batches of the given size, each its own transaction,
    and gives the pause function how long each batch took. Returns how many dedup records were deleted.
    """
    out = 0

    while True:

        batch_started = time.monotonic()

        with engine.begin() as connection:

            # The batch is selected first ..
            keys:'anylist' = []

            for row in connection.execute(_expired_query, {'now_ms': now_ms, 'batch_size': batch_size}):
                keys.append((row.kind, row.scope, row.message_id))

            # .. nothing expired is left so the sweep is done ..
            if not keys:
                break

            # .. and the delete repeats the condition, so that a dedup record that a publication renewed
            # .. after the select remains.
            delete = message_dedup_table.delete()
            delete = delete.where(and_(
                tuple_(*_key_columns).in_(keys),
                _columns.expires_ms <= now_ms,
            ))
            result = connection.execute(delete)

            out += result.rowcount

        # The pause between the batches is when the live traffic gets to write.
        pause_after_batch(time.monotonic() - batch_started)

        # A batch shorter than its size was the last one.
        if len(keys) < batch_size:
            break

    return out

# ################################################################################################################################
# ################################################################################################################################
