# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment every file transfer audit test runs under - the audit log pointed
# at a throwaway SQLite database for the duration of one test.

# stdlib
import os
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_sql.env import database_env
from zato.common.audit_log.api import event_link_table, event_table, get_audit_engine, ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist, intlist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-file-transfer-audit-server'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def audit_db_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def events_of_type(events:'anylist', event_type:'str') -> 'anylist':
    """ The events of one type, in the order they were written.
    """
    out:'anylist' = []

    for item in events:
        if item['event_type'] == event_type:
            out.append(item)

    return out

# ################################################################################################################################

def get_parents(event_id:'int') -> 'intlist':
    """ The ids of the events one event names as its parents.
    """
    engine = get_audit_engine()

    query = select(event_link_table.c.parent_event_id)
    query = query.where(event_link_table.c.child_event_id == event_id)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################
