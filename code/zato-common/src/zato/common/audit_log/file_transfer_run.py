# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Constants and audit database queries of a file transfer run.

from __future__ import annotations

# stdlib
from datetime import timedelta
from json import dumps, loads

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_table, get_audit_engine, AuditBody, \
    AuditEvent, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, intnone, stranydict
    anydict = anydict
    anylist = anylist
    intnone = intnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The reasons a run skips a directory entry.
Skip_Not_A_File        = 'not-a-file'
Skip_Claim_File        = 'claim-file'
Skip_Marker_File       = 'marker-file'
Skip_Marker_Missing    = 'marker-missing'
Skip_Pattern_Mismatch  = 'pattern-mismatch'
Skip_Vanished          = 'vanished'
Skip_Size_Changed      = 'size-changed'
Skip_Mtime_Changed     = 'mtime-changed'
Skip_Claimed_Elsewhere = 'claimed-elsewhere'
Skip_Retry_Backoff     = 'retry-backoff'

# The name of each skip reason, read in a table or on a chip.
Skip_Reason_Name = {
    Skip_Not_A_File:        'Not a file',
    Skip_Claim_File:        'Claimed by a consumer',
    Skip_Marker_File:       'Marker file',
    Skip_Marker_Missing:    'Marker missing',
    Skip_Pattern_Mismatch:  'Pattern mismatch',
    Skip_Vanished:          'Vanished',
    Skip_Size_Changed:      'Size changed',
    Skip_Mtime_Changed:     'Modified',
    Skip_Claimed_Elsewhere: 'Claimed elsewhere',
    Skip_Retry_Backoff:     'Retry backoff',
}

# The label of each skip reason, read in a sentence after its count.
Skip_Reason_Label = {
    Skip_Not_A_File:        'not files',
    Skip_Claim_File:        'claimed by a consumer',
    Skip_Marker_File:       'marker files',
    Skip_Marker_Missing:    'marker not arrived yet',
    Skip_Pattern_Mismatch:  'did not match the pattern',
    Skip_Vanished:          'gone before it could be read',
    Skip_Size_Changed:      'still being uploaded, size changed',
    Skip_Mtime_Changed:     'still being uploaded, modified',
    Skip_Claimed_Elsewhere: 'claimed by another consumer first',
    Skip_Retry_Backoff:     'waiting for its next attempt',
}

# The decisions a run records about an entry in its ledger.
Decision_Taken       = 'taken'
Decision_Skipped     = 'skipped'
Decision_Failed      = 'failed'
Decision_Quarantined = 'quarantined'

# The run statuses, kept in the status column of the run's row.
Run_Status_Running      = 'running'
Run_Status_Clean        = 'clean'
Run_Status_Partial      = 'partial'
Run_Status_Failed       = 'failed'
Run_Status_Empty        = 'empty'
Run_Status_Unchanged    = 'unchanged'
Run_Status_No_Directory = 'no-directory'
Run_Status_List_Failed  = 'list-failed'
Run_Status_Interrupted  = 'interrupted'

# The phases of a run, kept in its data while it runs.
Phase_Connecting         = 'connecting'
Phase_Checking_Directory = 'checking-directory'
Phase_Listing            = 'listing'
Phase_Waiting            = 'waiting'
Phase_Claiming           = 'claiming'
Phase_Reading            = 'reading'
Phase_Delivering         = 'delivering'
Phase_Acking             = 'acking'
Phase_Done               = 'done'

# How many entries a ledger records in full.
Run_Ledger_Max_Entries = 500

# How far back a run looks for earlier failures of the same file name.
Retry_Memory_Days = 7

# How far back a run looks for an earlier delivery of the same bytes.
Seen_Before_Window_Days = 30

# The note of a run interrupted by a server stop.
Interrupted_Note = 'Server stopped during run'

# The attribute names the queries below match on.
_attr_checksum = 'checksum'
_attr_schedule = 'schedule'

# ################################################################################################################################
# ################################################################################################################################

def iso_days_ago(days:'int') -> 'str':
    """ The ISO timestamp of the given number of days ago.
    """
    now = utcnow()
    then = now - timedelta(days=days)

    out = then.isoformat()
    return out

# ################################################################################################################################

def build_ledger_record(
    name:'str',
    size:'int',
    last_modified_iso:'str',
    decision:'str',
    *,
    reason:'str' = '',
    file_cid:'str' = '',
    duration_ms:'int' = 0,
    attempt:'int' = 0,
    next_attempt_iso:'str' = '',
    ) -> 'stranydict':
    """ One record of a run's ledger.
    """
    out:'stranydict' = {
        'name': name,
        'size': size,
        'last_modified_iso': last_modified_iso,
        'decision': decision,
        'reason': reason,
        'file_cid': file_cid,
        'duration_ms': duration_ms,
        'attempt': attempt,
        'next_attempt_iso': next_attempt_iso,
    }

    return out

# ################################################################################################################################

def update_run_event(
    event_id:'intnone',
    *,
    outcome:'str' = '',
    status:'str' = '',
    duration_ms:'intnone' = None,
    data:'stranydict | None' = None,
    ) -> 'None':
    """ Updates the given columns of a run's row.
    """
    if event_id is None:
        return

    values:'stranydict' = {}

    if outcome:
        values['outcome'] = outcome

    if status:
        values['status'] = status

    if duration_ms is not None:
        values['duration_ms'] = duration_ms

    if data is not None:
        values['data'] = dumps(data)

    if not values:
        return

    statement = event_table.update()
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(**values)

    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def write_run_ledger(event_id:'intnone', event_time_iso:'str', records:'anylist') -> 'None':
    """ Stores the first Run_Ledger_Max_Entries records as the run's ledger body.
    """
    if event_id is None:
        return

    kept = records[:Run_Ledger_Max_Entries]
    data = dumps(kept)

    _write_body(event_id, AuditBody.Run_Ledger, event_time_iso, data)

# ################################################################################################################################

def write_run_error(event_id:'intnone', event_time_iso:'str', error:'str') -> 'None':
    """ Stores the traceback of a run as its error body.
    """
    if event_id is None:
        return

    _write_body(event_id, AuditBody.Error, event_time_iso, error)

# ################################################################################################################################

def _write_body(event_id:'int', kind:'str', event_time_iso:'str', data:'str') -> 'None':
    statement = event_body_table.insert()
    statement = statement.values(event_id=event_id, kind=kind, event_time_iso=event_time_iso, data=data)

    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def load_attempt_memory(conn_name:'str', schedule_name:'str', since_iso:'str') -> 'anydict':
    """ The failures of each file name of a schedule since the given moment, keyed by file name.
    A File_Retried event resets the file's count.
    """

    # Our response to produce
    out:'anydict' = {}

    remembered_types = [AuditEvent.Delivery_Failed, AuditEvent.File_Retried]

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_conn = event_table.c.object_name == conn_name
    is_remembered = event_table.c.event_type.in_(remembered_types)
    is_recent = event_table.c.event_time_iso >= since_iso

    statement = select(event_table.c.event_type, event_table.c.event_time_iso, event_table.c.data)
    statement = statement.where(and_(is_source, is_conn, is_remembered, is_recent))
    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    for event_type, event_time_iso, data in rows:

        details = loads(data)

        # The connection may run several schedules.
        if details['schedule'] != schedule_name:
            continue

        file_name = details['file_name']

        # A retried file starts counting from zero ..
        if event_type == AuditEvent.File_Retried:
            out.pop(file_name, None)
            continue

        # .. and every failure adds to the count.
        if memory := out.get(file_name):
            memory['attempts'] += 1
            memory['last_failed_iso'] = event_time_iso
        else:
            out[file_name] = {
                'attempts': 1,
                'first_failed_iso': event_time_iso,
                'last_failed_iso': event_time_iso,
            }

    return out

# ################################################################################################################################

def find_seen_before(conn_name:'str', schedule_name:'str', checksum:'str', since_iso:'str') -> 'stranydict | None':
    """ The newest delivery of the same checksum by the same schedule since the given moment, or None.
    """
    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_conn = event_table.c.object_name == conn_name
    is_delivered = event_table.c.event_type == AuditEvent.Delivered
    is_recent = event_table.c.event_time_iso >= since_iso
    is_checksum_attr = event_attr_table.c.name == _attr_checksum
    is_same_checksum = event_attr_table.c.value == checksum

    newest_first = event_table.c.id.desc()

    statement = select(event_table.c.id, event_table.c.event_time_iso, event_table.c.data)
    statement = statement.select_from(attr_join)
    statement = statement.where(and_(is_source, is_conn, is_delivered, is_recent, is_checksum_attr, is_same_checksum))
    statement = statement.order_by(newest_first)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    for event_id, event_time_iso, data in rows:

        details = loads(data)

        if details['schedule'] == schedule_name:
            out = {
                'event_id': event_id,
                'event_time_iso': event_time_iso,
                'file_name': details['file_name'],
            }
            break
    else:
        out = None

    return out

# ################################################################################################################################

def count_delivered_since(conn_name:'str', schedule_name:'str', since_iso:'str') -> 'int':
    """ How many files a schedule delivered since the given moment.
    """
    attr_join = event_table.join(event_attr_table, event_table.c.id == event_attr_table.c.event_id)
    delivered_count = func.count(event_table.c.id)

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_conn = event_table.c.object_name == conn_name
    is_delivered = event_table.c.event_type == AuditEvent.Delivered
    is_recent = event_table.c.event_time_iso >= since_iso
    is_schedule_attr = event_attr_table.c.name == _attr_schedule
    is_same_schedule = event_attr_table.c.value == schedule_name

    statement = select(delivered_count)
    statement = statement.select_from(attr_join)
    statement = statement.where(and_(is_source, is_conn, is_delivered, is_recent, is_schedule_attr, is_same_schedule))

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.scalar()

    if out is None:
        out = 0

    return out

# ################################################################################################################################

def find_running_runs(conn_name:'str', schedule_name:'str', server_name:'str') -> 'anylist':
    """ The (id, data) pairs of the schedule's runs this server still has marked as running.
    """

    # Our response to produce
    out:'anylist' = []

    is_source = event_table.c.source == AuditSource.File_Outgoing
    is_conn = event_table.c.object_name == conn_name
    is_run = event_table.c.event_type == AuditEvent.Run_Completed
    is_running = event_table.c.outcome == AuditOutcome.Running
    is_server = event_table.c.server_name == server_name

    statement = select(event_table.c.id, event_table.c.data)
    statement = statement.where(and_(is_source, is_conn, is_run, is_running, is_server))
    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    for event_id, data in rows:

        details = loads(data)

        if details['schedule'] == schedule_name:
            out.append((event_id, details))

    return out

# ################################################################################################################################
# ################################################################################################################################
