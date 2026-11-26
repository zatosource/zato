# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from collections import OrderedDict
from functools import partial
from logging import getLogger
from time import monotonic

# gevent
from gevent.monkey import get_original

# SQLAlchemy

# Zato
from zato.common.audit_log.attr_rows import build_attr_rows
from zato.common.audit_log.bulk_insert import insert_pending_events
from zato.common.audit_log.classification import derive_classification
from zato.common.audit_log.common import AuditBody, AuditClassification, AuditEvent, AuditLink, AuditOutcome, AuditSource, \
    Env_Commit_Max_Events, Env_Retention_Days, Env_Retention_Days_Prefix, event_attr_table, event_body_table, \
    event_link_table, event_table, get_commit_max_events, get_retention_days, get_source_env_suffix, metadata, \
    Status_Outstanding
from zato.common.audit_log.export.state import get_audit_export
from zato.common.audit_log.payload import prepare_payloads
from zato.common.audit_log.pending import PendingEvent
from zato.common.audit_log.retention import Env_Archive_Dir, Env_Content_Retention_Days, \
    Env_Content_Retention_Days_Prefix, Env_Retention_Interval_Seconds, get_content_retention_days, \
    get_retention_interval_seconds, register_prunability, run_retention
from zato.common.audit_log.retention_runner import request_retention
from zato.common.audit_log.search_index_merge import get_search_index_merger
from zato.common.config_db import Default_Enabled, Env_Audit_Log_Enabled
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.database import get_database_engine
from zato.common.audit_log.writes import write_audit
from zato.common.db_env.engine import call_database
from zato.common.db_env.pg8000_common import deferred_replies
from zato.common.pubsub.delivery_scope import get_delivery_scope
from zato.common.util.api import as_bool, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection, Engine
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import anylist, anylistnone, intlist, intlistnone, intnone, stranydict, strdictnone

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    anylistnone = anylistnone
    Connection = Connection
    datetime = datetime
    Engine = Engine
    intlist = intlist
    intlistnone = intlistnone
    intnone = intnone
    pending_event_list = pending_event_list
    stranydict = stranydict
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

# The public names of this module - the audit log's one-stop API surface
__all__ = [
    'build_attr_rows', 'derive_classification', 'event_attr_table', 'event_body_table', 'event_link_table',
    'event_table', 'get_content_retention_days', 'get_retention_days',
    'get_source_env_suffix', 'is_audit_log_enabled', 'metadata', 'register_prunability',
    'AuditBody', 'AuditClassification', 'AuditEvent', 'AuditLink', 'AuditLog', 'AuditOutcome', 'AuditSource', 'ModuleCtx',
    'Retention_Days', 'Status_Outstanding',
]

# ################################################################################################################################
# ################################################################################################################################

# How much of a group commit's capacity each event takes - the capacity is counted in events
_commit_event_weight = 1

# The NUL character, which no text column of PostgreSQL can hold, and what replaces it in the text of an event,
# the same replacement character that stands for the bytes of a binary body that cannot be decoded
_nul_character = '\x00'
_nul_replacement = '\ufffd'

# ################################################################################################################################
# ################################################################################################################################

def _replace_nul(text:'str') -> 'str':
    """ Returns the text with each NUL character replaced, so that PostgreSQL accepts it.
    """
    out = text.replace(_nul_character, _nul_replacement)
    return out

# ################################################################################################################################

def _insert_links(connection:'Connection', rows:'anylist') -> 'None':
    """ Inserts the lineage links of an event in the transaction of the connection.
    """
    insert_statement = event_link_table.insert()
    _ = connection.execute(insert_statement, rows)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable turning the whole audit log off
    Env_Enabled = Env_Audit_Log_Enabled

    # The environment variables overriding how long events and their content are kept,
    # process-wide and, with the source name appended, for one source alone
    Env_Retention_Days                = Env_Retention_Days
    Env_Content_Retention_Days        = Env_Content_Retention_Days
    Env_Retention_Days_Prefix         = Env_Retention_Days_Prefix
    Env_Content_Retention_Days_Prefix = Env_Content_Retention_Days_Prefix
    Env_Archive_Dir                   = Env_Archive_Dir

    # The environment variable configuring how many seconds pass between the retention runs that commits request
    Env_Retention_Interval_Seconds = Env_Retention_Interval_Seconds

    # The environment variable configuring the group commit of synchronous writes
    Env_Commit_Max_Events = Env_Commit_Max_Events

    # The audit log records events unless it is turned off explicitly
    Default_Enabled = Default_Enabled

# ################################################################################################################################
# ################################################################################################################################

# A lock of the threads of the operating system, which gevent does not replace
_allocate_thread_lock = get_original('_thread', 'allocate_lock')

logger = getLogger(__name__)

# Per-write trace diagnostics - opt-in through the environment
_trace_flag = os.environ.get('Zato_HL7_Trace')
_is_trace_enabled = bool(_trace_flag)

def _trace(message:'str', *args:'object') -> 'None':
    if _is_trace_enabled:
        logger.info('TRACE ' + message, *args)

# How many distinct cids have their sequence counters kept in memory at a time
_max_tracked_cids = 100_000

# What the process was configured with at startup - display code uses this constant
Retention_Days = get_retention_days()

# ################################################################################################################################
# ################################################################################################################################

def is_audit_log_enabled() -> 'bool':
    """ Whether the audit log records anything at all. Read on each write rather than cached, so turning
    the switch off takes effect at once, with no restart and with no need to rebuild any writer.
    """

    # An unset variable means the audit log is on
    if value := os.environ.get(ModuleCtx.Env_Enabled, ''):
        out = as_bool(value)
    else:
        out = ModuleCtx.Default_Enabled

    return out

# ################################################################################################################################
# ################################################################################################################################

class AuditLog:
    """ A source-agnostic audit log writing structured events into the Zato database. Each event is committed
    before the call that writes it returns. The whole log can be turned off through Zato_Audit_Log_Enabled,
    in which case every insert becomes a silent no-op.
    """

    def __init__(self, server_name:'str') -> 'None':

        self.server_name = server_name

        # A commit requests a retention run once the interval has passed since the previous request,
        # and the first request follows the first interval after the start
        self._retention_interval = get_retention_interval_seconds()
        self._next_retention_at = monotonic() + self._retention_interval

        # Per-cid sequence counters - ordered so the least recently used ones can be dropped. The lock is a thread lock,
        # because the pub/sub writer builds events in the thread of its transaction.
        self._cid_sequence:'OrderedDict' = OrderedDict()
        self._cid_sequence_lock = _allocate_thread_lock()

        # The writes of concurrent callers share their commits, each caller submitting a list of events
        commit_max_events = get_commit_max_events()

        self._commit_queue = CommitQueue(
            write_batch=self._write_event_lists,
            max_weight=commit_max_events,
        )

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine of the Zato database, resolved on each access, with the cache in db_env making the lookup cheap.
        """
        out = get_database_engine()
        return out

# ################################################################################################################################

    def insert(
        self,
        source:'str',
        event_type:'str',
        object_name:'str',
        *,
        cid:'str' = '',
        msg_id:'str' = '',
        correl_id:'str' = '',
        ext_client_id:'str' = '',
        pub_time:'datetime | None' = None,
        endpoint:'str' = '',
        sub_key:'str' = '',
        size:'int' = 0,
        priority:'int' = 0,
        outcome:'str' = '',
        application_outcome:'str' = '',
        classification:'str' = '',
        status:'str' = '',
        duration_ms:'int' = 0,
        data:'str' = '',
        attrs:'strdictnone' = None,
        bodies:'strdictnone' = None,
        attachments:'anylistnone' = None,
        parents:'intlistnone' = None,
        parent_link_type:'str' = AuditLink.Resubmit_Of,
        is_export_payload_active:'bool' = False,
        commits_with_batch:'bool' = False,
        ) -> 'intnone':
        """ Writes one audit event, at the moment it happens, in the same process, commits it before the call returns
        and returns its id. An event marked with commits_with_batch that is written in a push delivery batch commits
        with the acknowledgement of the batch instead, and None is returned. Nothing is written and None is returned
        when the audit log is turned off. The payload leaves the process with the OTLP export only if
        is_export_payload_active is set.
        """

        # A turned-off audit log records nothing at all - the event is dropped in silence,
        # with no message of its own, so no caller has to know whether the log is in use
        if not is_audit_log_enabled():
            return None

        pending = self.new_pending_event(source, event_type, object_name, cid=cid, msg_id=msg_id, correl_id=correl_id,
            ext_client_id=ext_client_id, pub_time=pub_time, endpoint=endpoint, sub_key=sub_key, size=size,
            priority=priority, outcome=outcome, application_outcome=application_outcome, classification=classification,
            status=status, duration_ms=duration_ms, data=data, attrs=attrs, bodies=bodies, attachments=attachments,
            parents=parents, parent_link_type=parent_link_type, is_export_payload_active=is_export_payload_active)

        # An event that records how a message of a push delivery batch concluded commits with the acknowledgement ..
        if commits_with_batch:
            if scope := get_delivery_scope():
                scope.audit_events.append(pending)
                return None

        # .. while any other event is committed before the call returns.
        self._commit_queue.write([pending], weight=_commit_event_weight, is_urgent=False)

        out = pending.event_id
        return out

# ################################################################################################################################

    def new_pending_event(
        self,
        source:'str',
        event_type:'str',
        object_name:'str',
        *,
        cid:'str' = '',
        msg_id:'str' = '',
        correl_id:'str' = '',
        ext_client_id:'str' = '',
        pub_time:'datetime | None' = None,
        endpoint:'str' = '',
        sub_key:'str' = '',
        size:'int' = 0,
        priority:'int' = 0,
        outcome:'str' = '',
        application_outcome:'str' = '',
        classification:'str' = '',
        status:'str' = '',
        duration_ms:'int' = 0,
        data:'str' = '',
        internal_data:'str' = '',
        attrs:'strdictnone' = None,
        bodies:'strdictnone' = None,
        attachments:'anylistnone' = None,
        parents:'intlistnone' = None,
        parent_link_type:'str' = AuditLink.Resubmit_Of,
        is_export_payload_active:'bool' = False,
        ) -> 'PendingEvent':
        """ Returns one audit event with everything that is written alongside it, for a writer
        that commits it in a transaction of its own choosing.
        """

        # The event time is always assigned here so all rows share one clock ..
        event_time = utcnow()

        # .. events sharing a cid carry an explicit sequence so their order is never ambiguous ..
        if cid:
            cid_sequence = self._get_next_cid_sequence(cid)
        else:
            cid_sequence = 0

        # .. failures are classified for the resubmit workflow unless the caller already knows better ..
        if not classification:
            classification = derive_classification(outcome, status, application_outcome)

        # .. optional companions default to empty ..
        if attrs is None:
            attrs = {}

        if bodies is None:
            bodies = {}

        # .. the text of the event, e.g. a response decoded from binary data, may contain NUL characters ..
        bodies = {kind: _replace_nul(body) for kind, body in bodies.items()}

        status = _replace_nul(status)
        data = _replace_nul(data)
        internal_data = _replace_nul(internal_data)

        if attachments is None:
            attachments = []

        if parents is None:
            parents = []

        # .. and package the event up with everything that is written alongside it.
        pending = PendingEvent()

        pending.attrs = attrs
        pending.bodies = bodies
        pending.attachments = attachments
        pending.parents = parents
        pending.parent_link_type = parent_link_type
        pending.is_export_payload_active = is_export_payload_active

        pending.values = {
            'cid': cid,
            'cid_sequence': cid_sequence,
            'source': source,
            'event_type': event_type,
            'object_name': object_name,
            'msg_id': msg_id,
            'correl_id': correl_id,
            'ext_client_id': ext_client_id,
            'pub_time': pub_time,
            'event_time': event_time,
            'server_name': self.server_name,
            'endpoint': endpoint,
            'sub_key': sub_key,
            'size': size,
            'priority': priority,
            'outcome': outcome,
            'application_outcome': application_outcome,
            'classification': classification,
            'status': status,
            'duration_ms': duration_ms,
            'data': data,
            'internal_data': internal_data,
        }

        return pending

# ################################################################################################################################

    def write_events(self, batch:'pending_event_list') -> 'None':
        """ Writes the events that one operation produced together, in one transaction,
        and nothing when the audit log is turned off.
        """
        if not is_audit_log_enabled():
            return

        self.write_pending(batch)

# ################################################################################################################################

    def write_pending(self, batch:'pending_event_list') -> 'None':
        """ Writes events that one operation collected, in one transaction shared with the synchronous writes
        of concurrent callers.
        """
        batch_size = len(batch)

        weight = batch_size * _commit_event_weight
        self._commit_queue.write(batch, weight=weight, is_urgent=False)

# ################################################################################################################################

    def _write_event_lists(self, event_lists:'anylist') -> 'intnone':
        """ Writes the lists of events of the callers of one group commit in a single transaction.
        """
        batch:'pending_event_list' = []

        for event_list in event_lists:
            batch.extend(event_list)

        out = self._write_batch(batch)
        return out

# ################################################################################################################################

    def add_links(self, child_event_id:'int', parents:'intlist', link_type:'str') -> 'None':
        """ Links an already written event to its parent events - how a resubmission points back
        to the original message it was born from. A turned-off audit log has no event to link to,
        so the call is skipped in silence, the same way the insert that preceded it was.
        """
        if not is_audit_log_enabled():
            return

        rows:'anylist' = []

        for parent_event_id in parents:
            rows.append({
                'child_event_id': child_event_id,
                'parent_event_id': parent_event_id,
                'link_type': link_type,
            })

        _ = write_audit(self.engine, _insert_links, rows)

# ################################################################################################################################

    def _get_next_cid_sequence(self, cid:'str') -> 'int':
        """ Returns the next sequence number for this cid, monotonic within this writer.
        """

        with self._cid_sequence_lock:

            # Advance this cid's counter, starting a new one if we have not seen it ..
            if cid in self._cid_sequence:
                out = self._cid_sequence[cid] + 1
            else:
                out = 1

            self._cid_sequence[cid] = out
            self._cid_sequence.move_to_end(cid)

            # .. and forget the least recently used cid once there are too many.
            tracked_count = len(self._cid_sequence)

            if tracked_count > _max_tracked_cids:
                _ = self._cid_sequence.popitem(last=False)

        return out

# ################################################################################################################################

    def _build_attr_rows(self, event_id:'int', attrs:'stranydict') -> 'anylist':
        out = build_attr_rows(event_id, attrs)
        return out

# ################################################################################################################################

    def _write_batch(self, batch:'pending_event_list') -> 'intnone':
        """ Writes one batch of events in a single transaction, along with their attributes,
        bodies and lineage links. Returns the id of the last event written, or None if the audit log was turned off
        after the events were accepted, in which case none of them is written.
        """
        if not self.prepare_commit():
            return None

        # Trace point 9: every database transaction with its size and duration
        write_start = monotonic()

        out = self.commit_batch(batch)

        write_elapsed = monotonic() - write_start
        write_elapsed_ms = write_elapsed * 1000
        batch_size = len(batch)

        _trace('db write of %d events done %.1fms', batch_size, write_elapsed_ms)

        self.complete_commit(batch)

        return out

# ################################################################################################################################

    def prepare_commit(self) -> 'bool':
        """ Runs what precedes a commit of events, in this process or in the transaction of another writer,
        and returns whether the audit log is turned on. The switch is read on each commit, and the writer
        of a commit for which it is off writes none of its events.
        """
        out = is_audit_log_enabled()

        # The search indexes of the database the events go to are merged in the background
        if out:
            _ = get_search_index_merger(self.engine)

        return out

# ################################################################################################################################

    def complete_commit(self, batch:'pending_event_list') -> 'None':
        """ Runs what follows a commit of events, in this process or in the transaction of another writer.
        """
        batch_size = len(batch)

        # Events the database accepted go out to the OTLP collector too, if this process exports them.
        # The export is looked up here rather than held by the writer because writers are built
        # in many places, and this way all of them share the one export the process has.
        if export := get_audit_export():
            try:
                export.emit_batch(batch)
            except Exception:
                logger.exception('Audit export could not take a batch of %d events', batch_size)

        # Rows older than the retention window are deleted in the background, once per interval.
        now = monotonic()

        if now >= self._next_retention_at:
            self._next_retention_at = now + self._retention_interval
            request_retention(self.engine)

# ################################################################################################################################

    def commit_batch(self, batch:'pending_event_list') -> 'int':
        """ Commits one batch of events in this process and returns the id of the last event written.
        """
        # The payloads of the batch are prepared before the transaction begins ..
        prepare = partial(prepare_payloads, batch)

        # .. and the events are inserted with them.
        out = call_database(self.engine, self._insert_batch, batch, prepare=prepare)
        return out

# ################################################################################################################################

    def _insert_batch(self, batch:'pending_event_list') -> 'int':
        """ Inserts one batch of events in a single transaction, with one statement per table,
        and returns the id of the last event written.
        """
        with self.engine.begin() as connection, deferred_replies(connection):
            event_ids = insert_pending_events(connection, batch)

        out = event_ids[-1]
        return out

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Enforces both retention tiers - early content pruning and row deletion.
        """
        run_retention(self.engine, now)

# ################################################################################################################################
# ################################################################################################################################
