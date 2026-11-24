# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment every file transfer audit test runs under - the audit log pointed
# at a throwaway PostgreSQL database for the duration of one test.

# stdlib
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_link_table, event_table
from zato.common.audit_log.common import event_data
from zato.common.db_env.database import get_database_engine
from zato.common.test.zato_database import zato_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anylist, intlist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-file-transfer-audit-server'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def audit_db_env() -> 'envgen':
    """ Points the audit log at a throwaway PostgreSQL database for the duration of a test.
    """
    with zato_database_engine():
        yield

# ################################################################################################################################

def get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_database_engine()

    query = select(event_table, event_data)
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
    engine = get_database_engine()

    query = select(event_link_table.c.parent_event_id)
    query = query.where(event_link_table.c.child_event_id == event_id)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################
