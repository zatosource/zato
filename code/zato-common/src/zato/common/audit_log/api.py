# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
from datetime import timedelta
from logging import getLogger

# Zato
from zato.common.defaults import default_env_base_dir
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding all audit events, shared by all sources
audit_db_file_name = 'audit.db'

# ################################################################################################################################
# ################################################################################################################################

class AuditSource:
    PubSub = 'pubsub'

# ################################################################################################################################

class AuditEvent:
    Published = 'published'
    Delivered = 'delivered'
    Delivery_Failed = 'delivery-failed'
    Expired = 'expired'
    Received = 'received'

# ################################################################################################################################

class AuditOutcome:
    OK = 'ok'
    Error = 'error'
    Expired = 'expired'

# How many days of events are kept
_retention_days = 30

# Retention runs after every that many inserts
_retention_check_interval = 1000

# ################################################################################################################################
# ################################################################################################################################

_schema = """
create table if not exists event (
    id integer primary key,
    cid text,
    source text,
    event_type text,
    object_name text,
    msg_id text,
    correl_id text,
    ext_client_id text,
    pub_time_iso text,
    event_time_iso text,
    server_name text,
    endpoint text,
    sub_key text,
    size integer,
    priority integer,
    outcome text,
    data text
)
"""

_index_object = 'create index if not exists idx_event_source_object on event (source, object_name, id)'
_index_cid = 'create index if not exists idx_event_cid on event (cid, id)'

_insert_sql = """
insert into event (
    cid, source, event_type, object_name, msg_id, correl_id, ext_client_id,
    pub_time_iso, event_time_iso, server_name, endpoint, sub_key, size, priority, outcome, data
) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_retention_sql = "delete from event where event_time_iso < ?"

# ################################################################################################################################
# ################################################################################################################################

def get_audit_db_path() -> 'str':
    """ Returns the full path to the shared audit database file.
    """
    out = os.path.join(default_env_base_dir, audit_db_file_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AuditLog:
    """ A source-agnostic audit log writing structured events into one shared SQLite database.
    Pub/sub is the first covered source, other sources plug in by passing a different source value.
    """

    def __init__(self, server_name:'str') -> 'None':

        self.server_name = server_name

        # Counts inserts so retention can run periodically instead of on every write
        self._insert_count = 0

        # The environment directory may not exist yet, e.g. in freshly created environments ..
        os.makedirs(default_env_base_dir, exist_ok=True)

        # .. open the shared database file ..
        db_path = get_audit_db_path()
        self.conn = sqlite3.connect(db_path)

        # .. WAL mode lets multiple server processes and the web-admin reader share the file safely,
        # .. and synchronous=NORMAL keeps each insert fast while remaining durable enough for audit data ..
        _ = self.conn.execute('pragma journal_mode=wal')
        _ = self.conn.execute('pragma synchronous=normal')

        # .. and make sure the schema exists.
        _ = self.conn.execute(_schema)
        _ = self.conn.execute(_index_object)
        _ = self.conn.execute(_index_cid)
        self.conn.commit()

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
        data:'str' = '',
        ) -> 'None':
        """ Writes one audit event, at the moment it happens, in the same process.
        A plain insert inside WAL is microseconds so no queue or background thread is needed.
        """

        # The event time is always assigned here so all rows share one clock ..
        now = utcnow()
        event_time_iso = now.isoformat()

        # .. write the event ..
        _ = self.conn.execute(_insert_sql, (
            cid, source, event_type, object_name, msg_id, correl_id, ext_client_id,
            pub_time_iso, event_time_iso, self.server_name, endpoint, sub_key, size, priority, outcome, data,
        ))
        self.conn.commit()

        # .. and periodically delete rows older than the retention window.
        self._insert_count += 1

        if self._insert_count % _retention_check_interval == 0:
            self._run_retention(now)

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Deletes events older than the retention window.
        """
        cutoff = now - timedelta(days=_retention_days)
        cutoff_iso = cutoff.isoformat()

        cursor = self.conn.execute(_retention_sql, (cutoff_iso,))
        self.conn.commit()

        if cursor.rowcount:
            logger.info('Audit log retention deleted %d event(s) older than %s', cursor.rowcount, cutoff_iso)

# ################################################################################################################################
# ################################################################################################################################
