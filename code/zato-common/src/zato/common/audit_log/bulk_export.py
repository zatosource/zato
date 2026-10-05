# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Audit database queries of FHIR bulk export jobs - a job is the set of events sharing one cid.

from __future__ import annotations

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.api import HL7
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, dictlist, stranydict, strlist
    anylist = anylist
    dictlist = dictlist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# How many of a connection's most recent jobs a page lists.
Max_Jobs = 100

# The attribute names the queries below read.
_attr_phase = 'phase'
_attr_count = 'count'

# ################################################################################################################################
# ################################################################################################################################

def _new_job(job_id:'str') -> 'stranydict':
    """ One job of the list, before its events are read into it.
    """
    out:'stranydict' = {
        'job_id': job_id,
        'started_iso': '',
        'finished_iso': '',
        'status': _bulk.Status.Running,
        'phase': '',
        'files': 0,
        'resources': 0,
        'errors': 0,
        'error': '',
    }

    return out

# ################################################################################################################################

def _find_recent_job_ids(conn_name:'str') -> 'strlist':
    """ The ids of a connection's most recent jobs, newest first.
    """
    newest_event_id = func.max(event_table.c.id)

    is_source = event_table.c.source == AuditSource.FHIR_Bulk_Export
    is_conn = event_table.c.object_name == conn_name

    statement = select(event_table.c.cid)
    statement = statement.where(and_(is_source, is_conn))
    statement = statement.group_by(event_table.c.cid)
    statement = statement.order_by(newest_event_id.desc())
    statement = statement.limit(Max_Jobs)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    out:'strlist' = []

    for row in rows:
        out.append(row[0])

    return out

# ################################################################################################################################

def _read_events(job_ids:'strlist') -> 'anylist':
    """ Every event of the given jobs along with its phase and count, oldest first.
    """
    is_source = event_table.c.source == AuditSource.FHIR_Bulk_Export
    is_job = event_table.c.cid.in_(job_ids)

    statement = select(
        event_table.c.id,
        event_table.c.cid,
        event_table.c.event_type,
        event_table.c.event_time_iso,
        event_table.c.outcome,
        event_table.c.data,
    )
    statement = statement.where(and_(is_source, is_job))
    statement = statement.order_by(event_table.c.id)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.fetchall()

    return out

# ################################################################################################################################

def _read_attrs(event_ids:'anylist') -> 'stranydict':
    """ The phase and count of each event, keyed by event id.
    """
    is_event = event_attr_table.c.event_id.in_(event_ids)
    is_wanted = event_attr_table.c.name.in_([_attr_phase, _attr_count])

    statement = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value)
    statement = statement.where(and_(is_event, is_wanted))

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    out:'stranydict' = {}

    for event_id, name, value in rows:
        attrs = out.setdefault(event_id, {_attr_phase: '', _attr_count: '0'})
        attrs[name] = value

    return out

# ################################################################################################################################

def _apply_event(job:'stranydict', event_type:'str', event_time_iso:'str', outcome:'str', data:'str',
    attrs:'stranydict') -> 'None':
    """ Reads one event into the job it belongs to.
    """

    # The first event of a job is when it started ..
    if not job['started_iso']:
        job['started_iso'] = event_time_iso

    # .. the newest one names the phase the job is in ..
    job['phase'] = attrs[_attr_phase]

    # .. each file received adds to the file and resource counts ..
    if event_type == AuditEvent.Received:
        if outcome == AuditOutcome.OK:
            job['files'] += 1
            job['resources'] += int(attrs[_attr_count])

    # .. and anything that went wrong is counted, with the newest message kept.
    if outcome == AuditOutcome.Error:
        job['errors'] += 1
        job['error'] = data

    # The job's last event closes it.
    if event_type == AuditEvent.Run_Completed:
        job['finished_iso'] = event_time_iso
        if outcome == AuditOutcome.OK:
            job['status'] = _bulk.Status.Done
        else:
            job['status'] = _bulk.Status.Failed

# ################################################################################################################################

def get_job_list(conn_name:'str') -> 'dictlist':
    """ The most recent bulk export jobs of a connection, newest first.
    """

    # Our response to produce
    out:'dictlist' = []

    job_ids = _find_recent_job_ids(conn_name)

    if not job_ids:
        return out

    events = _read_events(job_ids)

    event_ids = []
    for event in events:
        event_ids.append(event[0])

    attrs_by_event = _read_attrs(event_ids)

    jobs_by_id:'stranydict' = {}
    for job_id in job_ids:
        jobs_by_id[job_id] = _new_job(job_id)

    for event_id, job_id, event_type, event_time_iso, outcome, data in events:
        job = jobs_by_id[job_id]
        attrs = attrs_by_event[event_id]
        _apply_event(job, event_type, event_time_iso, outcome, data, attrs)

    for job_id in job_ids:
        out.append(jobs_by_id[job_id])

    return out

# ################################################################################################################################
# ################################################################################################################################
