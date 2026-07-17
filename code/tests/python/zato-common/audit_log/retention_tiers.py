# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta
from shutil import rmtree
from tempfile import mkdtemp

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, register_prunability, AuditEvent, AuditLink, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.retention import Env_Archive_Dir, Env_Content_Retention_Days
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, strdictnone

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anydictnone = anydictnone
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The channel the retention test events belong to
_channel_name = 'audit.test.retention'

# A source whose registered predicate protects all its content regardless of age
_protected_source = 'audit-test-protected'

# How many days of message content the scenario keeps
_content_retention_days = 7

# Old enough for content pruning but too recent for row deletion
_content_expired_age_days = 12

# Old enough for row deletion
_row_expired_age_days = 45

# ################################################################################################################################
# ################################################################################################################################

def _insert_event_at(
    audit_log:'AuditLog',
    age_days:'int',
    *,
    source:'str' = AuditSource.X12,
    outcome:'str' = AuditOutcome.OK,
    data:'str' = '',
    attrs:'strdictnone' = None,
    bodies:'strdictnone' = None,
    ) -> 'int':
    """ Writes one event through the audit log and then backdates it by the given number of days -
    retention only ever looks at the event time.
    """
    event_id = audit_log.insert(source, AuditEvent.Interchange_Sent, _channel_name,
        cid=f'cid-retention-{age_days}-{outcome}', outcome=outcome, data=data, attrs=attrs, bodies=bodies)

    event_time = utcnow() - timedelta(days=age_days)
    event_time_iso = event_time.isoformat()

    engine = get_audit_engine()

    backdate_event = event_table.update()
    backdate_event = backdate_event.where(event_table.c.id == event_id)
    backdate_event = backdate_event.values(event_time_iso=event_time_iso)

    backdate_bodies = event_body_table.update()
    backdate_bodies = backdate_bodies.where(event_body_table.c.event_id == event_id)
    backdate_bodies = backdate_bodies.values(event_time_iso=event_time_iso)

    with engine.begin() as connection:
        _ = connection.execute(backdate_event)
        _ = connection.execute(backdate_bodies)

    out = event_id
    return out

# ################################################################################################################################

def _get_event_row(event_id:'int') -> 'anydictnone':
    """ Returns one event row as a dict, or None if it no longer exists.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.id == event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    if row:
        out = dict(row._mapping)
    else:
        out = None

    return out

# ################################################################################################################################

def _count_rows(table:'any_', event_id_column:'any_', event_id:'int') -> 'int':
    """ Counts the rows of one companion table that reference one event.
    """
    engine = get_audit_engine()

    query = select(func.count())
    query = query.select_from(table)
    query = query.where(event_id_column == event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = result.scalar()

    return out

# ################################################################################################################################

def _never_prune(row:'anydict') -> 'bool':
    """ The predicate of a source that never allows its content to be pruned.
    """
    return False

# ################################################################################################################################
# ################################################################################################################################

def run_retention_tiers_scenario() -> 'None':
    """ The tiered-retention scenario every backend must pass: content pruning ahead
    of row deletion, per-source prunability predicates protecting what must not be pruned,
    companion rows deleted together with their events, and archive files written before anything is lost.
    """
    delete_all_events()

    audit_log = AuditLog(_server_name)

    # Everything retention prunes or deletes is archived into this directory first
    archive_dir = mkdtemp(prefix='zato-audit-log-archive-')

    os.environ[Env_Content_Retention_Days] = f'{_content_retention_days}'
    os.environ[Env_Archive_Dir] = archive_dir

    try:

        # A successful event past the content cutoff - its payload goes, its row stays ..
        prunable_id = _insert_event_at(audit_log, _content_expired_age_days,
            data='the payload retention prunes',
            attrs={'control_number': '000000101'},
            bodies={'request': 'the body retention prunes'})

        # .. a failure of the same age - the default predicate protects it ..
        failed_id = _insert_event_at(audit_log, _content_expired_age_days,
            outcome=AuditOutcome.Error, data='the payload an operator still needs')

        # .. an event of a source whose own predicate protects everything ..
        register_prunability(_protected_source, _never_prune)

        protected_id = _insert_event_at(audit_log, _content_expired_age_days,
            source=_protected_source, data='the payload the predicate protects')

        # .. an event past the row cutoff, with companions that must disappear with it ..
        expired_id = _insert_event_at(audit_log, _row_expired_age_days,
            data='the payload of a row past the retention window',
            attrs={'control_number': '000000102'},
            bodies={'request': 'the body of a row past the retention window'})

        # .. a recent event linked to the expired one - the link goes when its parent does ..
        recent_id = _insert_event_at(audit_log, 0, data='a recent payload retention never touches')
        audit_log.add_links(recent_id, [expired_id], AuditLink.Resubmit_Of)

        # .. run retention the same way periodic inserts do ..
        now = utcnow()
        audit_log._run_retention(now)

        # .. the prunable event kept its row, attributes and outcome but lost its content ..
        row = _get_event_row(prunable_id)
        assert row is not None
        assert row['data'] == ''
        assert row['outcome'] == AuditOutcome.OK
        assert _count_rows(event_attr_table, event_attr_table.c.event_id, prunable_id) == 1
        assert _count_rows(event_body_table, event_body_table.c.event_id, prunable_id) == 0

        # .. the failure kept everything ..
        row = _get_event_row(failed_id)
        assert row is not None
        assert row['data'] == 'the payload an operator still needs'

        # .. so did the source with its own predicate ..
        row = _get_event_row(protected_id)
        assert row is not None
        assert row['data'] == 'the payload the predicate protects'

        # .. the expired event is gone along with its attributes, bodies and links ..
        assert _get_event_row(expired_id) is None
        assert _count_rows(event_attr_table, event_attr_table.c.event_id, expired_id) == 0
        assert _count_rows(event_body_table, event_body_table.c.event_id, expired_id) == 0
        assert _count_rows(event_link_table, event_link_table.c.parent_event_id, expired_id) == 0

        # .. the recent event was never touched ..
        row = _get_event_row(recent_id)
        assert row is not None
        assert row['data'] == 'a recent payload retention never touches'

        # .. and everything that was pruned or deleted went to the archive first.
        archive_files = os.listdir(archive_dir)
        assert len(archive_files) == 1, archive_files

        archive_path = os.path.join(archive_dir, archive_files[0])

        with open(archive_path, encoding='utf-8') as archive_file:
            archive_content = archive_file.read()

        assert 'the payload retention prunes' in archive_content
        assert 'the body retention prunes' in archive_content
        assert 'the payload of a row past the retention window' in archive_content
        assert 'the body of a row past the retention window' in archive_content
        assert 'a recent payload retention never touches' not in archive_content

    finally:
        _ = os.environ.pop(Env_Content_Retention_Days, None)
        _ = os.environ.pop(Env_Archive_Dir, None)
        rmtree(archive_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
