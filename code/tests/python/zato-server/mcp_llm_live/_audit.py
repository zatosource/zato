# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, AuditSource
from zato.common.audit_log.common import get_event_column

# Zato - test helpers
from live_environment.audit import new_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.sql import Select
    from zato.common.typing_ import anylist, dictlist, strnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The columns the assertions read, in the order the select below returns them
_event_columns = ('id', 'source', 'event_type', 'object_name', 'cid', 'endpoint', 'ext_client_id', 'sub_key',
    'size', 'outcome', 'data')

# How long to wait for expected audit rows to land, in seconds
_wait_timeout = 10

# How often to poll for them, in seconds
_wait_poll_interval = 0.2

# ################################################################################################################################
# ################################################################################################################################

def _new_event_query(min_id:'int') -> 'Select':
    """ A select of the MCP audit events newer than the given row ID, with the columns the assertions read.
    """
    columns:'anylist' = []

    for name in _event_columns:
        column = get_event_column(name)
        columns.append(column)

    out = select(*columns)
    out = out.where(event_table.c.source == AuditSource.MCP)
    out = out.where(event_table.c.id > min_id)

    return out

# ################################################################################################################################

def _run_event_query(database_env:'strstrdict', query:'Select') -> 'dictlist':
    """ Runs a select of audit events against the live server's Zato database and returns each row as a dict,
    with the data column parsed into a dict.
    """
    engine = new_database_engine(database_env)

    try:
        with engine.connect() as connection:
            db_rows = connection.execute(query).fetchall()
    finally:
        engine.dispose()

    out:'dictlist' = []

    for db_row in db_rows:
        row = dict(db_row._mapping)
        row['data'] = loads(row['data'])
        out.append(row)

    return out

# ################################################################################################################################

def read_events(
    database_env:'strstrdict',
    object_name:'strnone' = None,
    event_type:'strnone' = None,
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Reads MCP audit events out of the live server's Zato database, oldest first,
    optionally narrowed to one gateway and one event type. The data column comes back
    parsed into a dict.
    """
    query = _new_event_query(min_id)

    if object_name:
        query = query.where(event_table.c.object_name == object_name)

    if event_type:
        query = query.where(event_table.c.event_type == event_type)

    query = query.order_by(event_table.c.id)

    out = _run_event_query(database_env, query)
    return out

# ################################################################################################################################

def read_events_page(
    database_env:'strstrdict',
    object_name:'str',
    limit:'int',
    offset:'int',
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Reads one page of a gateway's MCP audit events, newest first - the ordering
    and the offset arithmetic the listings use.
    """
    query = _new_event_query(min_id)
    query = query.where(event_table.c.object_name == object_name)
    query = query.order_by(event_table.c.id.desc())
    query = query.limit(limit).offset(offset)

    out = _run_event_query(database_env, query)
    return out

# ################################################################################################################################

def last_event_id(database_env:'strstrdict') -> 'int':
    """ The highest event ID written so far, so a test can look only at the rows
    its own traffic produces.
    """
    events = read_events(database_env)

    if events:
        out = events[-1]['id']
    else:
        out = 0

    return out

# ################################################################################################################################

def wait_for_events(
    database_env:'strstrdict',
    expected_count:'int',
    object_name:'strnone' = None,
    event_type:'strnone' = None,
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Polls until at least the expected number of matching events lands, then returns them all.
    """
    deadline = time.monotonic() + _wait_timeout

    while time.monotonic() < deadline:

        out = read_events(database_env, object_name=object_name, event_type=event_type, min_id=min_id)

        if len(out) >= expected_count:
            return out

        time.sleep(_wait_poll_interval)

    out = read_events(database_env, object_name=object_name, event_type=event_type, min_id=min_id)

    raise Exception(f'Expected at least {expected_count} audit events, found {len(out)}: {out}')

# ################################################################################################################################
# ################################################################################################################################
