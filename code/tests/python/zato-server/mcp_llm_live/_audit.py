# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import time
from json import loads

# Zato
from zato.common.audit_log.api import AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, dictlist, strnone

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

def read_events(
    audit_db_path:'str',
    object_name:'strnone' = None,
    event_type:'strnone' = None,
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Reads MCP audit events out of the live server's audit database, oldest first,
    optionally narrowed to one gateway and one event type. The data column comes back
    parsed into a dict.
    """

    # An empty result before the server ever wrote an event - the file does not exist yet
    if not os.path.isfile(audit_db_path):
        return []

    column_list = ', '.join(_event_columns)

    query = f'select {column_list} from event where source = ? and id > ?'
    query_args:'anylist' = [AuditSource.MCP, min_id]

    if object_name:
        query += ' and object_name = ?'
        query_args.append(object_name)

    if event_type:
        query += ' and event_type = ?'
        query_args.append(event_type)

    query += ' order by id'

    connection = sqlite3.connect(audit_db_path)

    try:
        cursor = connection.execute(query, query_args)
        db_rows = cursor.fetchall()
    finally:
        connection.close()

    out:'dictlist' = []

    for db_row in db_rows:
        row = dict(zip(_event_columns, db_row))
        row['data'] = loads(row['data'])
        out.append(row)

    return out

# ################################################################################################################################

def read_events_page(
    audit_db_path:'str',
    object_name:'str',
    limit:'int',
    offset:'int',
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Reads one page of a gateway's MCP audit events, newest first - the ordering
    and the offset arithmetic the listings use.
    """

    column_list = ', '.join(_event_columns)

    query_filter = f'select {column_list} from event where source = ? and id > ? and object_name = ?'
    query = query_filter + ' order by id desc limit ? offset ?'
    query_args:'anylist' = [AuditSource.MCP, min_id, object_name, limit, offset]

    connection = sqlite3.connect(audit_db_path)

    try:
        cursor = connection.execute(query, query_args)
        db_rows = cursor.fetchall()
    finally:
        connection.close()

    out:'dictlist' = []

    for db_row in db_rows:
        row = dict(zip(_event_columns, db_row))
        row['data'] = loads(row['data'])
        out.append(row)

    return out

# ################################################################################################################################

def last_event_id(audit_db_path:'str') -> 'int':
    """ The highest event ID written so far, so a test can look only at the rows
    its own traffic produces.
    """
    events = read_events(audit_db_path)

    if events:
        out = events[-1]['id']
    else:
        out = 0

    return out

# ################################################################################################################################

def wait_for_events(
    audit_db_path:'str',
    expected_count:'int',
    object_name:'strnone' = None,
    event_type:'strnone' = None,
    min_id:'int' = 0,
    ) -> 'dictlist':
    """ Polls until at least the expected number of matching events lands, then returns them all.
    """
    deadline = time.monotonic() + _wait_timeout

    while time.monotonic() < deadline:

        out = read_events(audit_db_path, object_name=object_name, event_type=event_type, min_id=min_id)

        if len(out) >= expected_count:
            return out

        time.sleep(_wait_poll_interval)

    out = read_events(audit_db_path, object_name=object_name, event_type=event_type, min_id=min_id)

    raise Exception(f'Expected at least {expected_count} audit events, found {len(out)}: {out}')

# ################################################################################################################################
# ################################################################################################################################
