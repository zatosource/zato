# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from collections import OrderedDict
from logging import getLogger
from time import monotonic

# Zato
from zato.common.audit_log.buffer import Env_Flush_Max_Size, Env_Flush_Max_Wait_Ms, EventBuffer, get_flush_max_size, \
    get_flush_max_wait_ms, PendingEvent
from zato.common.audit_log.common import Attr_Value_Max_Len, Audit_DB_File_Name, AuditBody, AuditClassification, \
    AuditEvent, AuditLink, AuditOutcome, AuditSource, derive_classification, Env_Retention_Days, \
    Env_Retention_Days_Prefix, event_attr_table, event_body_table, event_link_table, event_table, get_retention_days, \
    get_source_env_suffix, metadata
from zato.common.audit_log.retention import Env_Archive_Dir, Env_Content_Retention_Days, \
    Env_Content_Retention_Days_Prefix, get_content_retention_days, register_prunability, run_retention
from zato.common.config_db import Default_Enabled, Env_Audit_Log_Enabled
from zato.common.db_env import Default_SSL, Default_SSL_Verify, Default_Type, EnvDBConfig, get_env_engine, \
    Type_MySQL, Type_Oracle, Type_PostgreSQL, Type_SQLite
from zato.common.util.api import as_bool, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.buffer import pending_event_list
    from zato.common.typing_ import anylist, intlist, intlistnone, intnone, stranydict, strdictnone

    # Dummy assignments to satisfy type checkers
    anylist = anylist
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
    'Audit_DB_File_Name', 'derive_classification', 'event_attr_table', 'event_body_table', 'event_link_table',
    'event_table', 'get_audit_db_path', 'get_audit_engine', 'get_content_retention_days', 'get_retention_days',
    'get_source_env_suffix', 'is_audit_log_enabled', 'metadata', 'register_prunability', 'AuditBody',
    'AuditClassification', 'AuditEvent', 'AuditLink', 'AuditLog', 'AuditOutcome', 'AuditSource', 'ModuleCtx',
    'Retention_Days',
]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable turning the whole audit log off
    Env_Enabled = Env_Audit_Log_Enabled

    # Environment variables selecting and configuring the audit log database
    Env_Type     = 'Zato_Audit_Log_DB_Type'
    Env_Host     = 'Zato_Audit_Log_DB_Host'
    Env_Port     = 'Zato_Audit_Log_DB_Port'
    Env_Username = 'Zato_Audit_Log_DB_Username'
    Env_Password = 'Zato_Audit_Log_DB_Password'
    Env_Name     = 'Zato_Audit_Log_DB_Name'

    # Environment variables configuring SSL/TLS for the audit log database
    Env_SSL           = 'Zato_Audit_Log_DB_SSL'
    Env_SSL_CA_File   = 'Zato_Audit_Log_DB_SSL_CA_File'
    Env_SSL_Cert_File = 'Zato_Audit_Log_DB_SSL_Cert_File'
    Env_SSL_Key_File  = 'Zato_Audit_Log_DB_SSL_Key_File'
    Env_SSL_Verify    = 'Zato_Audit_Log_DB_SSL_Verify'

    # The environment variables overriding how long events and their content are kept,
    # process-wide and, with the source name appended, for one source alone
    Env_Retention_Days                = Env_Retention_Days
    Env_Content_Retention_Days        = Env_Content_Retention_Days
    Env_Retention_Days_Prefix         = Env_Retention_Days_Prefix
    Env_Content_Retention_Days_Prefix = Env_Content_Retention_Days_Prefix
    Env_Archive_Dir                   = Env_Archive_Dir

    # The environment variables configuring the buffered writer
    Env_Flush_Max_Size    = Env_Flush_Max_Size
    Env_Flush_Max_Wait_Ms = Env_Flush_Max_Wait_Ms

    # Recognized database types
    Type_SQLite     = Type_SQLite
    Type_MySQL      = Type_MySQL
    Type_PostgreSQL = Type_PostgreSQL
    Type_Oracle     = Type_Oracle

    # The audit log records events unless it is turned off explicitly
    Default_Enabled = Default_Enabled

    # What is used when Zato_Audit_Log_DB_Type is not set
    Default_Type = Default_Type

    # SSL is off unless requested explicitly
    Default_SSL = Default_SSL

    # When SSL is on, the server certificate is verified unless turned off explicitly
    Default_SSL_Verify = Default_SSL_Verify

# ################################################################################################################################
# ################################################################################################################################

# Retention runs after every that many inserts
_retention_check_interval = 1000

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

# How the audit log database is selected and configured through the environment.
# The pool matters for SQLite too - without it every event opens and closes its own
# connection, and closing the last WAL connection runs a checkpoint with an fsync,
# which serializes high-volume producers like pub/sub behind disk flushes.
_env_config_options = {
    'env_prefix': 'Zato_Audit_Log_DB_',
    'sqlite_file_name': Audit_DB_File_Name,
    'metadata': metadata,
    'needs_pool': True,
}

_env_config = EnvDBConfig(**_env_config_options)

# ################################################################################################################################

def get_audit_db_path() -> 'str':
    """ Returns the full path to the default SQLite audit database file.
    """
    out = _env_config.get_sqlite_path()
    return out

# ################################################################################################################################

def get_audit_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the audit log database, creating the schema if needed.
    Which database is used comes from the Zato_Audit_Log_DB_* environment variables,
    defaulting to a shared SQLite file.
    """
    out = get_env_engine(_env_config)
    return out

# ################################################################################################################################

def is_audit_log_enabled() -> 'bool':
    """ Whether the audit log records anything at all, as set through the Config DB SQL screen.
    Read on each write rather than cached, so turning the switch off takes effect at once,
    with no restart and with no need to rebuild any writer.
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
    """ A source-agnostic audit log writing structured events into one shared database.
    The database is SQLite by default and can be MySQL, PostgreSQL or Oracle DB,
    as configured through the Zato_Audit_Log_DB_* environment variables.
    Events are written synchronously by default - high-volume producers turn on batching
    through the flush parameters or the Zato_Audit_Log_Flush_* environment variables.
    The whole log can be turned off through Zato_Audit_Log_Enabled, in which case every
    insert becomes a silent no-op.
    """

    def __init__(
        self,
        server_name:'str',
        *,
        flush_max_size:'intnone' = None,
        flush_max_wait_ms:'intnone' = None,
        ) -> 'None':

        self.server_name = server_name

        # Counts inserts so retention can run periodically instead of on every write
        self._insert_count = 0

        # Per-cid sequence counters - ordered so the least recently used ones can be dropped
        self._cid_sequence:'OrderedDict' = OrderedDict()

        # The flush configuration comes from the environment unless given explicitly ..
        if flush_max_size is None:
            flush_max_size = get_flush_max_size()

        if flush_max_wait_ms is None:
            flush_max_wait_ms = get_flush_max_wait_ms()

        self.flush_max_size = flush_max_size

        # .. and the buffer holds events between flushes.
        buffer_options = {
            'max_size': flush_max_size,
            'max_wait_ms': flush_max_wait_ms,
            'write_batch': self._write_batch,
        }

        self._buffer = EventBuffer(**buffer_options)

# ################################################################################################################################

    @property
    def engine(self) -> 'Engine':
        """ The engine behind the current Zato_Audit_Log_DB_* configuration - resolved on each
        access, with the per-configuration cache in db_env making the lookup cheap, so changing
        the variables at runtime redirects all new writes, the background flusher's included,
        to the new database.
        """
        out = get_audit_engine()
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
        pub_time_iso:'str' = '',
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
        parents:'intlistnone' = None,
        parent_link_type:'str' = AuditLink.Resubmit_Of,
        ) -> 'intnone':
        """ Writes one audit event, at the moment it happens, in the same process.
        Returns the event's id when the write is synchronous, None when it was buffered,
        and None without writing anything when the audit log is turned off.
        """

        # A turned-off audit log records nothing at all - the event is dropped in silence,
        # with no message of its own, so no caller has to know whether the log is in use
        if not is_audit_log_enabled():
            return None

        # The event time is always assigned here so all rows share one clock ..
        now = utcnow()
        event_time_iso = now.isoformat()

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

        if parents is None:
            parents = []

        # .. package the event up with everything that is written alongside it ..
        pending = PendingEvent()

        pending.attrs = attrs
        pending.bodies = bodies
        pending.parents = parents
        pending.parent_link_type = parent_link_type

        pending.values = {
            'cid': cid,
            'cid_sequence': cid_sequence,
            'source': source,
            'event_type': event_type,
            'object_name': object_name,
            'msg_id': msg_id,
            'correl_id': correl_id,
            'ext_client_id': ext_client_id,
            'pub_time_iso': pub_time_iso,
            'event_time_iso': event_time_iso,
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
        }

        # .. write it now if batching is off ..
        if self.flush_max_size <= 1:
            out = self._write_batch([pending])
            return out

        # .. or leave it in the buffer for the next flush.
        else:
            self._buffer.add(pending)
            return None

# ################################################################################################################################

    def flush(self) -> 'None':
        """ Writes out everything currently buffered. Events accepted while the audit log
        was still on are written out even after it has been turned off - they were recorded
        already, only their trip to the database was pending.
        """
        self._buffer.flush()

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

        insert_statement = event_link_table.insert()

        with self.engine.begin() as connection:
            _ = connection.execute(insert_statement, rows)

# ################################################################################################################################

    def _get_next_cid_sequence(self, cid:'str') -> 'int':
        """ Returns the next sequence number for this cid, monotonic within this writer.
        """

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
        """ Turns an attribute dict into rows - every value is stored as capped text
        and numbers additionally go to the numeric column for aggregation queries.
        """
        out:'anylist' = []

        for name, value in attrs.items():

            row:'stranydict' = {
                'event_id': event_id,
                'name': name,
                'value': '',
                'value_number': None,
            }

            # Real numbers are stored twice, and everything else is text -
            # numeric-looking strings such as identifiers with leading zeros stay text only.
            if isinstance(value, bool):
                row['value'] = str(value)
            elif isinstance(value, (int, float)):
                row['value'] = str(value)
                row['value_number'] = value
            else:
                value = str(value)
                row['value'] = value[:Attr_Value_Max_Len]

            out.append(row)

        return out

# ################################################################################################################################

    def _write_batch(self, batch:'pending_event_list') -> 'intnone':
        """ Writes one batch of events in a single transaction, along with their attributes,
        bodies and lineage links. Returns the id of the last event written.
        """

        # Our response to produce
        out:'intnone' = None

        # Trace point 9: every database transaction with its size and duration
        write_start = monotonic()

        with self.engine.begin() as connection:

            for pending in batch:

                # The event row itself comes first, so everything else can reference its id ..
                insert_statement = event_table.insert()
                insert_statement = insert_statement.values(**pending.values)

                result = connection.execute(insert_statement)

                primary_key = result.inserted_primary_key
                event_id = primary_key[0]
                out = event_id

                # .. searchable attributes ..
                if pending.attrs:
                    attr_rows = self._build_attr_rows(event_id, pending.attrs)
                    attr_insert = event_attr_table.insert()

                    _ = connection.execute(attr_insert, attr_rows)

                # .. message bodies, stamped with the event's own time so pruning never needs a join ..
                if pending.bodies:

                    body_rows:'anylist' = []

                    for kind, body_data in pending.bodies.items():
                        body_rows.append({
                            'event_id': event_id,
                            'kind': kind,
                            'event_time_iso': pending.values['event_time_iso'],
                            'data': body_data,
                        })

                    body_insert = event_body_table.insert()

                    _ = connection.execute(body_insert, body_rows)

                # .. and lineage links to parent events.
                if pending.parents:

                    link_rows:'anylist' = []

                    for parent_event_id in pending.parents:
                        link_rows.append({
                            'child_event_id': event_id,
                            'parent_event_id': parent_event_id,
                            'link_type': pending.parent_link_type,
                        })

                    link_insert = event_link_table.insert()

                    _ = connection.execute(link_insert, link_rows)

        write_elapsed = monotonic() - write_start
        write_elapsed_ms = write_elapsed * 1000
        batch_size = len(batch)

        _trace('db write of %d events done %.1fms', batch_size, write_elapsed_ms)

        # Periodically delete rows older than the retention window
        self._insert_count += batch_size

        if self._insert_count >= _retention_check_interval:
            self._insert_count = 0
            now = utcnow()

            # Trace point 10: the inline retention run, a suspect for long stalls
            _trace('retention run begins')
            retention_start = monotonic()

            self._run_retention(now)

            _trace('retention run done %.1fms', (monotonic() - retention_start) * 1000)

        return out

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Enforces both retention tiers - early content pruning and row deletion.
        """
        run_retention(self.engine, now)

# ################################################################################################################################
# ################################################################################################################################
