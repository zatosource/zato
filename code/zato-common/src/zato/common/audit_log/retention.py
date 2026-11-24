# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from base64 import b64encode
from datetime import datetime, timedelta
from json import dumps
from logging import getLogger

# SQLAlchemy
from sqlalchemy import or_, select, update

# Zato
from zato.common.audit_log.common import AuditOutcome, event_attr_table, event_body_table, event_data, event_link_table, \
    event_table, get_retention_days, get_source_env_suffix
from zato.common.audit_log.payload import delete_unreferenced_payloads
from zato.common.db_env.write_path import Mechanism, write_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, callable_, intlist, strcalldict, strlist, strnone

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    Engine = Engine
    any_ = any_
    anylist = anylist
    callable_ = callable_
    intlist = intlist
    strcalldict = strcalldict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The environment variable overriding how many days message content is kept - content may be pruned
# before the event rows themselves so an investigation still finds that a message existed,
# when and with what outcome, long after its payload is gone.
Env_Content_Retention_Days = 'Zato_Audit_Log_Content_Retention_Days'

# What one source's own content retention variable is prefixed with, completed the same way
# the row retention one is, e.g. Zato_Audit_Log_Content_Retention_Days_MLLP_CHANNEL.
Env_Content_Retention_Days_Prefix = 'Zato_Audit_Log_Content_Retention_Days_'

# The environment variable pointing at a directory to archive rows into before they are deleted
Env_Archive_Dir = 'Zato_Audit_Log_Archive_Dir'

# The sequence number of the first archive file of a second, which its name leaves out
Archive_First_Sequence = 1

# The permissions of an archive file, as a file that open creates
Archive_File_Mode = 0o666

# The environment variable overriding how many seconds pass between the retention runs that commits of events request
Env_Retention_Interval_Seconds = 'Zato_Audit_Log_Retention_Interval_Seconds'

# Content retention is off by default - content lives as long as the event rows do
_default_content_retention_days = 0

# How many seconds pass between the retention runs that commits of events request, unless configured otherwise
_default_retention_interval_seconds = 60

# How many rows are processed per statement during retention
_chunk_size = 500

# The number of chunks that a run without a limit writes in one call
_unlimited_chunks = sys.maxsize

# ################################################################################################################################

def get_content_retention_days(source:'str' = '') -> 'int':
    """ Returns how many days of message content are kept, for one source or, with no source named,
    process-wide. Zero means content is only pruned together with its event rows.
    """
    if source:

        suffix = get_source_env_suffix(source)
        env_name = f'{Env_Content_Retention_Days_Prefix}{suffix}'

        if value := os.environ.get(env_name, ''):
            out = int(value)
            return out

    if value := os.environ.get(Env_Content_Retention_Days, ''):
        out = int(value)
        return out

    out = _default_content_retention_days
    return out

# ################################################################################################################################

def get_retention_interval_seconds() -> 'int':
    """ Returns how many seconds pass between the retention runs that commits of events request.
    """
    if value := os.environ.get(Env_Retention_Interval_Seconds, ''):
        out = int(value)
    else:
        out = _default_retention_interval_seconds

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

# Sources that keep rows of their own next to their events register a function here that performs their retention
# in place of the generic one. The function takes the engine, the current time, the source and the archiver of the run,
# through which archive_events archives the events before the function deletes them.
_source_retention_registry:'strcalldict' = {}

# ################################################################################################################################

def register_source_retention(source:'str', func:'callable_') -> 'None':
    """ Registers the function that performs the retention of one source in place of the generic retention of its events.
    """
    _source_retention_registry[source] = func

# ################################################################################################################################
# ################################################################################################################################

def _archive_value(value:'datetime | bytes') -> 'str':
    """ Returns the JSON form of a column value JSON has no type for - a timestamp in ISO 8601
    and the bytes of an attachment in base64.
    """
    if isinstance(value, datetime):
        out = value.isoformat()
    else:
        out = b64encode(value).decode('ascii')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _sync_dir(path:'str') -> 'None':
    """ Syncs the entries of a directory to stable storage.
    """
    dir_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)

    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)

# ################################################################################################################################

def _make_archive_dir(path:'str') -> 'None':
    """ Creates the archive directory along with its missing ancestors, syncing the parent of each directory created.
    """
    missing:'strlist' = []

    # Collect the missing directories, from the innermost outward ..
    current = os.path.abspath(path)

    while not os.path.isdir(current):
        missing.append(current)
        current = os.path.dirname(current)

    # .. and create them from the outermost inward, each persisted in its parent.
    for dir_path in reversed(missing):

        try:
            os.mkdir(dir_path)
        except FileExistsError:
            continue

        parent_dir = os.path.dirname(dir_path)
        _sync_dir(parent_dir)

# ################################################################################################################################
# ################################################################################################################################

class Archiver:
    """ Writes rows to a JSON Lines archive file and syncs it to stable storage before they are deleted -
    active only when the archive directory is configured in the environment.
    """

    def __init__(self, now:'datetime') -> 'None':

        self.archive_dir = os.environ.get(Env_Archive_Dir, '')

        # The file is named after the moment this retention run started
        self.timestamp = now.strftime('%Y%m%d-%H%M%S')

        # The file of this run, which its first write creates
        self.archive_path:'strnone' = None

# ################################################################################################################################

    def is_active(self) -> 'bool':
        out = bool(self.archive_dir)
        return out

# ################################################################################################################################

    def _create_archive_file(self) -> 'str':
        """ Creates the archive file of this run, which no other run writes to. A run whose file name is taken,
        by a run that started within the same second, adds a sequence number to the name. The file and its entry
        in the directory are synced to stable storage before the method returns.
        """
        _make_archive_dir(self.archive_dir)

        sequence = Archive_First_Sequence

        while True:

            # The first name carries the timestamp alone, and each name after it a sequence number too ..
            if sequence == Archive_First_Sequence:
                file_name = f'audit-archive-{self.timestamp}.jsonl'
            else:
                file_name = f'audit-archive-{self.timestamp}-{sequence}.jsonl'

            archive_path = os.path.join(self.archive_dir, file_name)

            # .. the file is created only if no other run created it first ..
            try:
                archive_fd = os.open(archive_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, Archive_File_Mode)
            except FileExistsError:
                sequence += 1
            else:

                # .. and it is persisted along with its entry in the directory.
                try:
                    os.fsync(archive_fd)
                finally:
                    os.close(archive_fd)

                _sync_dir(self.archive_dir)

                return archive_path

# ################################################################################################################################

    def write_rows(self, kind:'str', rows:'anylist') -> 'None':
        """ Appends rows of one kind - event, body, attr, link or content - to the archive file and syncs the file
        to stable storage before returning, so that the rows are persisted before the retention deletes them.
        """
        if not rows:
            return

        if self.archive_path is None:
            self.archive_path = self._create_archive_file()

        with open(self.archive_path, 'a', encoding='utf-8') as archive_file:

            for row in rows:
                line = {'kind': kind}
                line.update(row)

                line_json = dumps(line, default=_archive_value)

                _ = archive_file.write(line_json)
                _ = archive_file.write('\n')

            # The rows are on stable storage before the deletion of the chunk is committed.
            archive_file.flush()
            os.fsync(archive_file.fileno())

# ################################################################################################################################
# ################################################################################################################################

class RetentionRun:
    """ One retention run, which proceeds through any number of calls of run_retention, each of which writes
    at most max_chunks chunks and records where the next call continues, so that other writes run between the calls.
    """

    def __init__(self, now:'datetime', max_chunks:'int') -> 'None':

        # The moment the cutoffs of the run are computed from
        self.now = now

        # The archive of the whole run
        self.archiver = Archiver(now)

        # How many chunks one call writes at most, and how many the call in progress may still write
        self.max_chunks = max_chunks
        self.chunks_left = max_chunks

        # The sources of the run, which its first call reads, and the position of the source in progress
        self.sources:'strlist' = []
        self.has_sources = False
        self.source_index = 0

        # The position of the content retention of the source in progress, and whether it is complete
        self.content_last_id = 0
        self.is_content_done = False

        # What the run did to the source in progress so far
        self.pruned_count = 0
        self.deleted_count = 0

        # Whether a source remains for the next call
        self.has_remaining_work = True

# ################################################################################################################################

    def has_chunks_left(self) -> 'bool':
        """ Returns whether the call in progress may write one more chunk.
        """
        out = self.chunks_left > 0
        return out

# ################################################################################################################################

    def next_source(self) -> 'None':
        """ Moves the run to its next source.
        """
        self.source_index += 1
        self.content_last_id = 0
        self.is_content_done = False
        self.pruned_count = 0
        self.deleted_count = 0

# ################################################################################################################################
# ################################################################################################################################

def _get_sources(engine:'Engine') -> 'strlist':
    """ Returns every source that has events in the log, because each of them is kept
    for its own number of days.
    """
    source_query = select(event_table.c.source)
    query = source_query.distinct()

    out:'strlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################

def _get_expired_ids(engine:'Engine', source:'str', cutoff:'datetime') -> 'intlist':
    """ Returns up to one chunk of ids of one source's events older than the cutoff, oldest first,
    so an event that closes an exchange never leaves a chunk ahead of the event that opened it.
    """
    query = select(event_table.c.id)
    query = query.where(event_table.c.source == source)
    query = query.where(event_table.c.event_time < cutoff)
    query = query.order_by(event_table.c.id)
    query = query.limit(_chunk_size)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    return out

# ################################################################################################################################

def _get_link_condition(ids:'intlist') -> 'any_':
    """ Returns the condition matching the lineage links in which any of the given events is the child or the parent.
    """
    is_child_event = event_link_table.c.child_event_id.in_(ids)
    is_parent_event = event_link_table.c.parent_event_id.in_(ids)

    out = or_(is_child_event, is_parent_event)
    return out

# ################################################################################################################################

def _archive_events(engine:'Engine', archiver:'Archiver', ids:'intlist') -> 'None':
    """ Archives full event rows, with their payloads, and their bodies, attributes and lineage links before deletion.
    """
    is_wanted_event = event_table.c.id.in_(ids)
    is_body_of_event = event_body_table.c.event_id.in_(ids)
    is_attr_of_event = event_attr_table.c.event_id.in_(ids)
    link_condition = _get_link_condition(ids)

    event_query = select(event_table, event_data)
    event_query = event_query.where(is_wanted_event)

    body_query = select(event_body_table)
    body_query = body_query.where(is_body_of_event)

    attr_query = select(event_attr_table)
    attr_query = attr_query.where(is_attr_of_event)

    link_query = select(event_link_table)
    link_query = link_query.where(link_condition)

    event_rows:'anylist' = []
    body_rows:'anylist' = []
    attr_rows:'anylist' = []
    link_rows:'anylist' = []

    with engine.connect() as connection:

        for row in connection.execute(event_query):
            event_row = dict(row._mapping)
            event_rows.append(event_row)

        for row in connection.execute(body_query):
            body_row = dict(row._mapping)
            body_rows.append(body_row)

        for row in connection.execute(attr_query):
            attr_row = dict(row._mapping)
            attr_rows.append(attr_row)

        for row in connection.execute(link_query):
            link_row = dict(row._mapping)
            link_rows.append(link_row)

    archiver.write_rows('event', event_rows)
    archiver.write_rows('body', body_rows)
    archiver.write_rows('attr', attr_rows)
    archiver.write_rows('link', link_rows)

# ################################################################################################################################

def archive_events(engine:'Engine', archiver:'Archiver', ids:'intlist') -> 'None':
    """ Archives the full rows of the given events with their bodies, attributes and lineage links
    when the archive directory is configured, for a source with a retention of its own,
    which calls it before it deletes the events.
    """
    if archiver.is_active():
        _archive_events(engine, archiver, ids)

# ################################################################################################################################

def _get_payload_ids(connection:'Connection', ids:'intlist') -> 'intlist':
    """ Returns the distinct ids of the payloads of the given events.
    """
    query = select(event_table.c.payload_id)
    query = query.where(event_table.c.id.in_(ids))
    query = query.where(event_table.c.payload_id.is_not(None))
    query = query.distinct()

    result = connection.execute(query)

    out = list(result.scalars())
    return out

# ################################################################################################################################

def _delete_events(engine:'Engine', ids:'intlist') -> 'None':
    """ Deletes one chunk of events along with their attributes, bodies and lineage links,
    and the payloads that no other event references.
    """
    link_condition = _get_link_condition(ids)

    is_attr_of_event = event_attr_table.c.event_id.in_(ids)
    is_body_of_event = event_body_table.c.event_id.in_(ids)
    is_wanted_event = event_table.c.id.in_(ids)

    delete_attrs = event_attr_table.delete()
    delete_attrs = delete_attrs.where(is_attr_of_event)

    delete_bodies = event_body_table.delete()
    delete_bodies = delete_bodies.where(is_body_of_event)

    delete_links = event_link_table.delete()
    delete_links = delete_links.where(link_condition)

    delete_events = event_table.delete()
    delete_events = delete_events.where(is_wanted_event)

    with engine.begin() as connection:

        # The payloads of the events are read before the events are gone ..
        payload_ids = _get_payload_ids(connection, ids)

        # .. everything that references the events is deleted along with them ..
        _ = connection.execute(delete_attrs)
        _ = connection.execute(delete_bodies)
        _ = connection.execute(delete_links)
        _ = connection.execute(delete_events)

        # .. and so are the payloads that no other event references.
        delete_unreferenced_payloads(connection, payload_ids)

# ################################################################################################################################

def _run_row_retention(engine:'Engine', run:'RetentionRun', source:'str', cutoff:'datetime') -> 'bool':
    """ Deletes one source's events older than its row-retention cutoff, chunk by chunk, archiving them first
    when an archive directory is configured. Returns whether none remains, which is not the case when the call
    in progress wrote all the chunks it may write.
    """
    while True:

        # A call that wrote all its chunks leaves the rest to the next call ..
        if not run.has_chunks_left():
            out = False
            break

        # .. otherwise, it takes one chunk of expired events ..
        ids = _get_expired_ids(engine, source, cutoff)

        if not ids:
            out = True
            break

        # .. archives them if archiving is on ..
        if run.archiver.is_active():
            _archive_events(engine, run.archiver, ids)

        # .. and deletes them along with everything that references them.
        _delete_events(engine, ids)

        deleted_count = len(ids)
        run.deleted_count += deleted_count
        run.chunks_left -= 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_content_candidates(engine:'Engine', source:'str', cutoff:'datetime', last_id:'int') -> 'anylist':
    """ Returns up to one chunk of one source's events older than the content cutoff that still
    carry content - a payload or rows in the body table.
    """
    has_body = select(event_body_table.c.id)
    has_body = has_body.where(event_body_table.c.event_id == event_table.c.id)

    has_any_body = has_body.exists()

    content_condition = or_(
        event_table.c.payload_id.is_not(None),
        has_any_body,
    )

    query = select(event_table.c.id, event_table.c.source, event_table.c.outcome, event_table.c.status)
    query = query.where(event_table.c.source == source)
    query = query.where(event_table.c.event_time < cutoff)
    query = query.where(event_table.c.id > last_id)
    query = query.where(content_condition)
    query = query.order_by(event_table.c.id)
    query = query.limit(_chunk_size)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            candidate = dict(row._mapping)
            out.append(candidate)

    return out

# ################################################################################################################################

def _archive_content(engine:'Engine', archiver:'Archiver', ids:'intlist') -> 'None':
    """ Archives the content of events whose payloads are about to be pruned.
    """
    is_wanted_event = event_table.c.id.in_(ids)
    is_body_of_event = event_body_table.c.event_id.in_(ids)

    content_query = select(event_table.c.id, event_data)
    content_query = content_query.where(is_wanted_event)
    content_query = content_query.where(event_table.c.payload_id.is_not(None))

    body_query = select(event_body_table)
    body_query = body_query.where(is_body_of_event)

    content_rows:'anylist' = []
    body_rows:'anylist' = []

    with engine.connect() as connection:

        for row in connection.execute(content_query):
            content_row = dict(row._mapping)
            content_rows.append(content_row)

        for row in connection.execute(body_query):
            body_row = dict(row._mapping)
            body_rows.append(body_row)

    archiver.write_rows('content', content_rows)
    archiver.write_rows('body', body_rows)

# ################################################################################################################################

def _prune_content(engine:'Engine', ids:'intlist') -> 'None':
    """ Prunes the content of one chunk of events - the events stop referencing their payloads, the payloads
    that no other event references are deleted and so are the body rows, while the event rows themselves stay.
    """
    is_wanted_event = event_table.c.id.in_(ids)
    is_body_of_event = event_body_table.c.event_id.in_(ids)

    prune_statement = update(event_table)
    prune_statement = prune_statement.where(is_wanted_event)
    prune_statement = prune_statement.values(payload_id=None)

    delete_bodies = event_body_table.delete()
    delete_bodies = delete_bodies.where(is_body_of_event)

    # The body rows are locked before the event rows, in the order that _delete_events locks them in,
    # because the retention of another server may delete the same events at the same time.
    with engine.begin() as connection:
        _ = connection.execute(delete_bodies)

        payload_ids = _get_payload_ids(connection, ids)
        _ = connection.execute(prune_statement)

        delete_unreferenced_payloads(connection, payload_ids)

# ################################################################################################################################

def _run_content_retention(engine:'Engine', run:'RetentionRun', source:'str', cutoff:'datetime') -> 'bool':
    """ Prunes the content of one source's events older than its content cutoff, keeping their
    metadata rows. The source's prunability predicate decides what is safe - unacknowledged
    or failed messages keep their content regardless of age. Returns whether no content to prune remains,
    which is not the case when the call in progress wrote all the chunks it may write.
    """
    while True:

        # A call that wrote all its chunks leaves the rest to the next call ..
        if not run.has_chunks_left():
            out = False
            break

        # .. otherwise, it takes one chunk of events that still have content ..
        candidates = _get_content_candidates(engine, source, cutoff, run.content_last_id)

        if not candidates:
            out = True
            break

        last_row = candidates[-1]
        run.content_last_id = last_row['id']

        # .. each source decides what is safe to prune ..
        ids:'intlist' = []

        for row in candidates:
            if is_content_prunable(row):
                ids.append(row['id'])

        if not ids:
            continue

        # .. archives the content if archiving is on ..
        if run.archiver.is_active():
            _archive_content(engine, run.archiver, ids)

        # .. and prunes it.
        _prune_content(engine, ids)

        pruned_count = len(ids)
        run.pruned_count += pruned_count
        run.chunks_left -= 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def _run_source_retention(engine:'Engine', run:'RetentionRun', source:'str') -> 'bool':
    """ Enforces both retention tiers for one source - content is pruned early while event rows,
    attributes and lineage survive until the row cutoff, so the audit trail outlives the payloads.
    Returns whether the source is complete, which is not the case when the call in progress wrote
    all the chunks it may write.
    """
    retention_days = get_retention_days(source)
    content_retention_days = get_content_retention_days(source)

    # Content retention only makes sense when it is shorter than row retention ..
    if not run.is_content_done:

        is_content_done = True

        if content_retention_days:
            if content_retention_days < retention_days:

                content_cutoff = run.now - timedelta(days=content_retention_days)
                is_content_done = _run_content_retention(engine, run, source, content_cutoff)

                if is_content_done:
                    if run.pruned_count:
                        suffix = 'event' if run.pruned_count == 1 else 'events'
                        logger.info('Audit log retention pruned content of %d %s %s older than %s',
                            run.pruned_count, source, suffix, content_cutoff)

        run.is_content_done = is_content_done

    # .. rows older than the row cutoff are deleted outright once the content is complete ..
    if run.is_content_done:

        row_cutoff = run.now - timedelta(days=retention_days)
        out = _run_row_retention(engine, run, source, row_cutoff)

        if out:
            if run.deleted_count:
                suffix = 'event' if run.deleted_count == 1 else 'events'
                logger.info('Audit log retention deleted %d %s %s older than %s',
                    run.deleted_count, source, suffix, row_cutoff)

    # .. and a call that has no chunks left for the content leaves the rows to the next call.
    else:
        out = False

    return out

# ################################################################################################################################

def _get_run_sources(engine:'Engine') -> 'strlist':
    """ Returns the sources of a run - every source with events and every source with a retention of its own.
    """
    out = _get_sources(engine)

    # A source with a retention of its own keeps rows outside the event table too, so it runs even without events.
    for source in _source_retention_registry:
        if source not in out:
            out.append(source)

    return out

# ################################################################################################################################

def run_retention(engine:'Engine', now:'datetime', run:'RetentionRun | None' = None) -> 'None':
    """ Enforces retention source by source, because each source is kept for its own number of days -
    a health check's pings age out well before the traffic events do. Without a run given, the whole run completes
    in this call, and with one, the call writes at most the chunks that the run allows and records in the run
    where the next call continues.
    """
    if run is None:
        run = RetentionRun(now, _unlimited_chunks)

    # Each call may write as many chunks as the run allows ..
    run.chunks_left = run.max_chunks

    # .. the first call of a run reads its sources ..
    if not run.has_sources:
        run.sources = _get_run_sources(engine)
        run.has_sources = True

    source_count = len(run.sources)

    with write_path(Mechanism.Maintenance):
        while run.source_index < source_count:

            source = run.sources[run.source_index]

            # .. a source with a retention of its own runs it as one chunk ..
            if source_retention := _source_retention_registry.get(source):

                if not run.has_chunks_left():
                    break

                source_retention(engine, run.now, source, run.archiver)
                run.chunks_left -= 1

            # .. any other source has its events deleted the generic way, as far as the chunks of the call allow ..
            elif not _run_source_retention(engine, run, source):
                break

            # .. and the run moves on to its next source.
            run.next_source()

    run.has_remaining_work = run.source_index < source_count

# ################################################################################################################################
# ################################################################################################################################
