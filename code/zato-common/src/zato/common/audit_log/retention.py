# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta
from json import dumps
from logging import getLogger

# SQLAlchemy
from sqlalchemy import or_, select, update

# Zato
from zato.common.audit_log.common import event_attr_table, event_body_table, event_link_table, event_table, \
    get_retention_days, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anylist, callable_, intlist, strcalldict

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    any_ = any_
    anylist = anylist
    callable_ = callable_
    datetime = datetime
    intlist = intlist
    strcalldict = strcalldict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The environment variable overriding how many days message content is kept - content may be pruned
# before the event rows themselves so an investigation still finds that a message existed,
# when and with what outcome, long after its payload is gone.
Env_Content_Retention_Days = 'Zato_Audit_Log_Content_Retention_Days'

# The environment variable pointing at a directory to archive rows into before they are deleted
Env_Archive_Dir = 'Zato_Audit_Log_Archive_Dir'

# Content retention is off by default - content lives as long as the event rows do
_default_content_retention_days = 0

# How many rows are processed per statement during retention
_chunk_size = 500

# ################################################################################################################################

def get_content_retention_days() -> 'int':
    """ Returns how many days of message content are kept. Zero means content is only pruned
    together with its event rows.
    """
    if value := os.environ.get(Env_Content_Retention_Days, ''):
        out = int(value)
    else:
        out = _default_content_retention_days

    return out

# ################################################################################################################################
# ################################################################################################################################

# Sources with their own idea of what is safe to prune register a predicate here.
# A predicate takes a row dict with the keys id, source, outcome and status,
# and returns True when the row's content may be pruned.
_prunability_registry:'strcalldict' = {}

# ################################################################################################################################

def register_prunability(source:'str', predicate:'callable_') -> 'None':
    """ Registers a predicate deciding whether the content of one source's events may be pruned -
    a source protects, for instance, messages that were sent but never acknowledged.
    """
    _prunability_registry[source] = predicate

# ################################################################################################################################

def is_content_prunable(row:'any_') -> 'bool':
    """ Returns True when the content of this event may be pruned. Age alone never prunes a failure -
    failed messages are precisely the ones an operator will want to inspect and resend.
    """
    if predicate := _prunability_registry.get(row['source']):
        out = predicate(row)
    else:
        out = row['outcome'] != AuditOutcome.Error

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Archiver:
    """ Writes rows to a JSON Lines archive file before they are deleted -
    active only when the archive directory is configured in the environment.
    """

    def __init__(self, now:'datetime') -> 'None':

        self.archive_dir = os.environ.get(Env_Archive_Dir, '')

        # The file is named after the moment this retention run started
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        self.archive_path = os.path.join(self.archive_dir, f'audit-archive-{timestamp}.jsonl')

# ################################################################################################################################

    def is_active(self) -> 'bool':
        out = bool(self.archive_dir)
        return out

# ################################################################################################################################

    def write_rows(self, kind:'str', rows:'anylist') -> 'None':
        """ Appends rows of one kind - event, body or content - to the archive file.
        """
        if not rows:
            return

        os.makedirs(self.archive_dir, exist_ok=True)

        with open(self.archive_path, 'a', encoding='utf-8') as archive_file:

            for row in rows:
                line = {'kind': kind}
                line.update(row)
                _ = archive_file.write(dumps(line))
                _ = archive_file.write('\n')

# ################################################################################################################################
# ################################################################################################################################

def _get_expired_ids(engine:'Engine', cutoff_iso:'str') -> 'intlist':
    """ Returns up to one chunk of ids of events older than the cutoff.
    """
    query = select(event_table.c.id)
    query = query.where(event_table.c.event_time_iso < cutoff_iso)
    query = query.limit(_chunk_size)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################

def _archive_events(engine:'Engine', archiver:'_Archiver', ids:'intlist') -> 'None':
    """ Archives full event rows and their bodies before deletion.
    """
    event_query = select(event_table)
    event_query = event_query.where(event_table.c.id.in_(ids))

    body_query = select(event_body_table)
    body_query = body_query.where(event_body_table.c.event_id.in_(ids))

    event_rows:'anylist' = []
    body_rows:'anylist' = []

    with engine.connect() as connection:

        for row in connection.execute(event_query):
            event_rows.append(dict(row._mapping))

        for row in connection.execute(body_query):
            body_rows.append(dict(row._mapping))

    archiver.write_rows('event', event_rows)
    archiver.write_rows('body', body_rows)

# ################################################################################################################################

def _delete_events(engine:'Engine', ids:'intlist') -> 'None':
    """ Deletes one chunk of events along with their attributes, bodies and lineage links.
    """
    link_condition = or_(
        event_link_table.c.child_event_id.in_(ids),
        event_link_table.c.parent_event_id.in_(ids),
    )

    with engine.begin() as connection:
        _ = connection.execute(event_attr_table.delete().where(event_attr_table.c.event_id.in_(ids)))
        _ = connection.execute(event_body_table.delete().where(event_body_table.c.event_id.in_(ids)))
        _ = connection.execute(event_link_table.delete().where(link_condition))
        _ = connection.execute(event_table.delete().where(event_table.c.id.in_(ids)))

# ################################################################################################################################

def _run_row_retention(engine:'Engine', archiver:'_Archiver', cutoff_iso:'str') -> 'int':
    """ Deletes events older than the row-retention cutoff, chunk by chunk, archiving them first
    when an archive directory is configured.
    """

    # Our count of deleted events
    out = 0

    while True:

        # Take one chunk of expired events ..
        ids = _get_expired_ids(engine, cutoff_iso)

        if not ids:
            break

        # .. archive them if archiving is on ..
        if archiver.is_active():
            _archive_events(engine, archiver, ids)

        # .. and delete them along with everything that references them.
        _delete_events(engine, ids)

        out += len(ids)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_content_candidates(engine:'Engine', cutoff_iso:'str', last_id:'int') -> 'anylist':
    """ Returns up to one chunk of events older than the content cutoff that still carry content -
    a non-empty data column or rows in the body table.
    """
    has_body = select(event_body_table.c.id)
    has_body = has_body.where(event_body_table.c.event_id == event_table.c.id)

    content_condition = or_(
        event_table.c.data != '',
        has_body.exists(),
    )

    query = select(event_table.c.id, event_table.c.source, event_table.c.outcome, event_table.c.status)
    query = query.where(event_table.c.event_time_iso < cutoff_iso)
    query = query.where(event_table.c.id > last_id)
    query = query.where(content_condition)
    query = query.order_by(event_table.c.id)
    query = query.limit(_chunk_size)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def _archive_content(engine:'Engine', archiver:'_Archiver', ids:'intlist') -> 'None':
    """ Archives the content of events whose payloads are about to be pruned.
    """
    content_query = select(event_table.c.id, event_table.c.data)
    content_query = content_query.where(event_table.c.id.in_(ids))
    content_query = content_query.where(event_table.c.data != '')

    body_query = select(event_body_table)
    body_query = body_query.where(event_body_table.c.event_id.in_(ids))

    content_rows:'anylist' = []
    body_rows:'anylist' = []

    with engine.connect() as connection:

        for row in connection.execute(content_query):
            content_rows.append(dict(row._mapping))

        for row in connection.execute(body_query):
            body_rows.append(dict(row._mapping))

    archiver.write_rows('content', content_rows)
    archiver.write_rows('body', body_rows)

# ################################################################################################################################

def _prune_content(engine:'Engine', ids:'intlist') -> 'None':
    """ Prunes the content of one chunk of events - the data column is emptied
    and their body rows are deleted, while the event rows themselves stay.
    """
    prune_statement = update(event_table)
    prune_statement = prune_statement.where(event_table.c.id.in_(ids))
    prune_statement = prune_statement.values(data='')

    with engine.begin() as connection:
        _ = connection.execute(prune_statement)
        _ = connection.execute(event_body_table.delete().where(event_body_table.c.event_id.in_(ids)))

# ################################################################################################################################

def _run_content_retention(engine:'Engine', archiver:'_Archiver', cutoff_iso:'str') -> 'int':
    """ Prunes the content of events older than the content cutoff, keeping their metadata rows.
    Each source's prunability predicate decides what is safe - unacknowledged or failed messages
    keep their content regardless of age.
    """

    # Our count of pruned events
    out = 0

    last_id = 0

    while True:

        # Take one chunk of events that still carry content ..
        candidates = _get_content_candidates(engine, cutoff_iso, last_id)

        if not candidates:
            break

        last_row = candidates[-1]
        last_id = last_row['id']

        # .. each source decides what is safe to prune ..
        ids:'intlist' = []

        for row in candidates:
            if is_content_prunable(row):
                ids.append(row['id'])

        if not ids:
            continue

        # .. archive the content if archiving is on ..
        if archiver.is_active():
            _archive_content(engine, archiver, ids)

        # .. and prune it.
        _prune_content(engine, ids)

        out += len(ids)

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_retention(engine:'Engine', now:'datetime') -> 'None':
    """ Enforces both retention tiers - content is pruned early while event rows,
    attributes and lineage survive until the row cutoff, so the audit trail outlives the payloads.
    """
    archiver = _Archiver(now)

    retention_days = get_retention_days()
    content_retention_days = get_content_retention_days()

    # Content retention only makes sense when it is shorter than row retention ..
    if content_retention_days:
        if content_retention_days < retention_days:

            content_cutoff = now - timedelta(days=content_retention_days)
            content_cutoff_iso = content_cutoff.isoformat()

            pruned_count = _run_content_retention(engine, archiver, content_cutoff_iso)

            if pruned_count:
                suffix = 'event' if pruned_count == 1 else 'events'
                logger.info('Audit log retention pruned content of %d %s older than %s',
                    pruned_count, suffix, content_cutoff_iso)

    # .. and rows older than the row cutoff are deleted outright.
    row_cutoff = now - timedelta(days=retention_days)
    row_cutoff_iso = row_cutoff.isoformat()

    deleted_count = _run_row_retention(engine, archiver, row_cutoff_iso)

    if deleted_count:
        suffix = 'event' if deleted_count == 1 else 'events'
        logger.info('Audit log retention deleted %d %s older than %s', deleted_count, suffix, row_cutoff_iso)

# ################################################################################################################################
# ################################################################################################################################
