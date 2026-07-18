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
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.audit_log.common import event_dedup_table
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist
    dictlist = dictlist
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

def build_dedup_key(action:'str', event_id:'int', payload:'str') -> 'str':
    """ Builds the dedup key of one resubmit - the same source event resubmitted
    with the same payload always hashes to the same key, while an edited payload
    is a different operation with a key of its own.
    """
    material = f'{action}:{event_id}:{payload}'
    out = sha256(material.encode('utf8')).hexdigest()

    return out

# ################################################################################################################################

def acquire_dedup_key(engine:'Engine', dedup_key:'str', cid:'str', action:'str') -> 'bool':
    """ Claims one dedup key before dispatch. Returns False when the key is already claimed,
    which means the same resubmit was applied - or started - before.
    """
    values = {
        'dedup_key': dedup_key,
        'cid': cid,
        'action': action,
        'created_iso': utcnow().isoformat(),
        'outcome': '',
        'completed_iso': '',
    }

    # The unique index makes the claim atomic - a concurrent duplicate loses here.
    # The catch is wide because drivers disagree on the class of a unique violation -
    # pg8000 rewraps its IntegrityError as OperationalError - so what happened
    # is confirmed by looking the key up, not by trusting the exception type.
    try:
        with engine.begin() as connection:
            _ = connection.execute(event_dedup_table.insert().values(**values))
    except DBAPIError:
        if _key_exists(engine, dedup_key):
            return False
        raise

    return True

# ################################################################################################################################

def _key_exists(engine:'Engine', dedup_key:'str') -> 'bool':
    """ Returns True when one dedup key is already claimed.
    """
    statement = select(event_dedup_table.c.id)
    statement = statement.where(event_dedup_table.c.dedup_key == dedup_key)

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    out = row is not None
    return out

# ################################################################################################################################

def complete_dedup_key(engine:'Engine', dedup_key:'str', outcome:'str') -> 'None':
    """ Records how the resubmit behind one claimed key ended.
    """
    statement = update(event_dedup_table)
    statement = statement.where(event_dedup_table.c.dedup_key == dedup_key)
    statement = statement.values(outcome=outcome, completed_iso=utcnow().isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def release_dedup_key(engine:'Engine', dedup_key:'str') -> 'None':
    """ Releases one claimed key - the path a failed resubmit takes, because a failure
    must remain retryable as-is, while a completed one remains claimed permanently.
    """
    statement = delete(event_dedup_table)
    statement = statement.where(event_dedup_table.c.dedup_key == dedup_key)

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def get_in_doubt(engine:'Engine') -> 'dictlist':
    """ Returns the resubmits that started but never recorded an outcome -
    what an interrupted bulk operation leaves behind, oldest first.
    """
    statement = select(
        event_dedup_table.c.dedup_key,
        event_dedup_table.c.cid,
        event_dedup_table.c.action,
        event_dedup_table.c.created_iso,
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
                'created_iso': row.created_iso,
            })

    return out

# ################################################################################################################################
# ################################################################################################################################
