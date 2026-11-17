# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resubmit dedup ledger - every resubmit acquires its key before dispatch,
# so a double-click or two overlapping bulk operations cannot double-apply one message
# downstream. Acquisition is atomic through a unique index, and a key acquired
# but never completed marks an interrupted resubmit, detectable as in-doubt
# rather than silently doubled or silently lost.

from __future__ import annotations

# stdlib
from hashlib import sha256

# SQLAlchemy
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

# Zato
from zato.common.audit_log.common import event_dedup_table
from zato.common.audit_log.writes import execute_audit_write, write_audit
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import dictlist, stranydict
    Connection = Connection
    dictlist = dictlist
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The insert of each database, which skips a row whose key exists already
_dialect_inserts = {
    Type_SQLite: sqlite_insert,
    Type_PostgreSQL: postgresql_insert,
}

# ################################################################################################################################
# ################################################################################################################################

def build_dedup_key(action:'str', event_id:'int', payload:'str') -> 'str':
    """ Builds the dedup key of one resubmit - the same source event resubmitted
    with the same payload always hashes to the same key, while an edited payload
    is a different operation with a key of its own.
    """
    material = f'{action}:{event_id}:{payload}'
    material_bytes = material.encode('utf8')
    digest = sha256(material_bytes)

    out = digest.hexdigest()

    return out

# ################################################################################################################################

def acquire_dedup_key(engine:'Engine', dedup_key:'str', cid:'str', action:'str', actor:'str'='') -> 'bool':
    """ Claims one dedup key before dispatch. Returns False when the key is already claimed,
    which means the same resubmit was applied - or started - before. The actor is who
    asked for the resubmit, so the ledger says not only what was resubmitted but by whom.
    """
    now = utcnow()

    values = {
        'dedup_key': dedup_key,
        'cid': cid,
        'action': action,
        'actor': actor,
        'created_at': now,
        'outcome': '',
        'completed_at': None,
    }

    out = write_audit(engine, _claim_key, values)
    return out

# ################################################################################################################################

def _claim_key(connection:'Connection', values:'stranydict') -> 'bool':
    """ Inserts the row of a dedup key in the transaction of the connection and returns whether it was inserted.
    The unique index makes the claim atomic - a concurrent duplicate inserts nothing, without failing the transaction
    that it shares with other writes.
    """
    insert = _dialect_inserts[connection.dialect.name]

    insert_statement = insert(event_dedup_table)
    insert_statement = insert_statement.values(**values)
    insert_statement = insert_statement.on_conflict_do_nothing(index_elements=[event_dedup_table.c.dedup_key])

    result = connection.execute(insert_statement)

    out = result.rowcount > 0
    return out

# ################################################################################################################################

def complete_dedup_key(engine:'Engine', dedup_key:'str', outcome:'str') -> 'None':
    """ Records how the resubmit behind one claimed key ended.
    """
    statement = update(event_dedup_table)
    statement = statement.where(event_dedup_table.c.dedup_key == dedup_key)
    now = utcnow()

    statement = statement.values(outcome=outcome, completed_at=now)

    _ = execute_audit_write(engine, statement)

# ################################################################################################################################

def release_dedup_key(engine:'Engine', dedup_key:'str') -> 'None':
    """ Releases one claimed key - the path a failed resubmit takes, because a failure
    must remain retryable as-is, while a completed one remains claimed permanently.
    """
    statement = delete(event_dedup_table)
    statement = statement.where(event_dedup_table.c.dedup_key == dedup_key)

    _ = execute_audit_write(engine, statement)

# ################################################################################################################################

def get_in_doubt(engine:'Engine') -> 'dictlist':
    """ Returns the resubmits that started but never recorded an outcome -
    what an interrupted bulk operation leaves behind, oldest first.
    """
    statement = select(
        event_dedup_table.c.dedup_key,
        event_dedup_table.c.cid,
        event_dedup_table.c.action,
        event_dedup_table.c.created_at,
    )
    statement = statement.where(event_dedup_table.c.outcome == '')
    statement = statement.order_by(event_dedup_table.c.id)

    out:'dictlist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append({
                'dedup_key': row.dedup_key,
                'cid': row.cid,
                'action': row.action,
                'created_at': row.created_at,
            })

    return out

# ################################################################################################################################
# ################################################################################################################################
