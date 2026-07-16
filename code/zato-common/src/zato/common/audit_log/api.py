# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import Column, Index, Integer, MetaData, String, Table, Text

# Zato
from zato.common.db_env import Default_SSL, Default_SSL_Verify, Default_Type, EnvDBConfig, get_env_engine, \
    Type_MySQL, Type_Oracle, Type_PostgreSQL, Type_SQLite
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    datetime = datetime
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding all audit events, shared by all sources
audit_db_file_name = 'audit.db'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

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

    # The environment variable overriding how many days of events are kept
    Env_Retention_Days = 'Zato_Audit_Log_Retention_Days'

    # Recognized database types
    Type_SQLite     = Type_SQLite
    Type_MySQL      = Type_MySQL
    Type_PostgreSQL = Type_PostgreSQL
    Type_Oracle     = Type_Oracle

    # What is used when Zato_Audit_Log_DB_Type is not set
    Default_Type = Default_Type

    # SSL is off unless requested explicitly
    Default_SSL = Default_SSL

    # When SSL is on, the server certificate is verified unless turned off explicitly
    Default_SSL_Verify = Default_SSL_Verify

# ################################################################################################################################
# ################################################################################################################################

# How many days of events are kept when the environment does not say otherwise
_default_retention_days = 30

# Retention runs after every that many inserts
_retention_check_interval = 1000

# Maximum length of short string columns
_short_column_len = 255

# Maximum length of the endpoint column - it may hold full addresses
_endpoint_column_len = 500

# ################################################################################################################################

def get_retention_days() -> 'int':
    """ Returns how many days of audit events are kept - also the widest window
    the reports run over. Configurable through an environment variable.
    """
    if value := os.environ.get(ModuleCtx.Env_Retention_Days, ''):
        out = int(value)
    else:
        out = _default_retention_days

    return out

# What the process was configured with at startup - display code uses this constant
Retention_Days = get_retention_days()

# ################################################################################################################################
# ################################################################################################################################

class AuditSource:
    PubSub        = 'pubsub'
    REST_Channel  = 'rest-channel'
    SOAP_Channel  = 'soap-channel'
    REST_Outgoing = 'rest-outgoing'
    SOAP_Outgoing = 'soap-outgoing'
    Email_IMAP    = 'email-imap'
    AS2           = 'as2'
    X12           = 'x12'
    MCP           = 'mcp'

# ################################################################################################################################

class AuditEvent:
    Published         = 'published'
    Delivered         = 'delivered'
    Delivery_Failed   = 'delivery-failed'
    Expired           = 'expired'
    Received          = 'received'
    Request_Received  = 'request-received'
    Response_Sent     = 'response-sent'
    Request_Sent      = 'request-sent'
    Response_Received = 'response-received'
    Message_Received  = 'message-received'
    Message_Marked_Seen = 'message-marked-seen'
    Message_Deleted     = 'message-deleted'
    Interchange_Sent     = 'interchange-sent'
    Interchange_Received = 'interchange-received'
    Ack_Sent             = 'ack-sent'
    Ack_Received         = 'ack-received'
    Message_Sent         = 'message-sent'
    MDN_Sent             = 'mdn-sent'
    MDN_Received         = 'mdn-received'
    Alert_Raised         = 'alert-raised'
    MCP_Initialize       = 'mcp-initialize'
    MCP_Tools_List       = 'mcp-tools-list'
    MCP_Tools_Call       = 'mcp-tools-call'
    MCP_Session_Delete   = 'mcp-session-delete'
    MCP_Batch            = 'mcp-batch'

# ################################################################################################################################

class AuditOutcome:
    OK      = 'ok'
    Error   = 'error'
    Expired = 'expired'

# ################################################################################################################################
# ################################################################################################################################

# The one table holding all audit events, portable across SQLite, MySQL, PostgreSQL and Oracle DB.
# Short columns are VARCHAR because MySQL cannot index TEXT columns without a prefix length.
metadata = MetaData()

event_table = Table('event', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('cid', String(_short_column_len)),
    Column('source', String(_short_column_len)),
    Column('event_type', String(_short_column_len)),
    Column('object_name', String(_short_column_len)),
    Column('msg_id', String(_short_column_len)),
    Column('correl_id', String(_short_column_len)),
    Column('ext_client_id', String(_short_column_len)),
    Column('pub_time_iso', String(_short_column_len)),
    Column('event_time_iso', String(_short_column_len)),
    Column('server_name', String(_short_column_len)),
    Column('endpoint', String(_endpoint_column_len)),
    Column('sub_key', String(_short_column_len)),
    Column('size', Integer),
    Column('priority', Integer),
    Column('outcome', String(_short_column_len)),
    Column('status', String(_short_column_len)),
    Column('duration_ms', Integer),
    Column('data', Text),
    Index('idx_event_source_object', 'source', 'object_name', 'id'),
    Index('idx_event_cid', 'cid', 'id'),
)

# ################################################################################################################################
# ################################################################################################################################

# How the audit log database is selected and configured through the environment
_env_config = EnvDBConfig(
    env_prefix='Zato_Audit_Log_DB_',
    sqlite_file_name=audit_db_file_name,
    metadata=metadata,
)

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
# ################################################################################################################################

class AuditLog:
    """ A source-agnostic audit log writing structured events into one shared database.
    The database is SQLite by default and can be MySQL, PostgreSQL or Oracle DB,
    as configured through the Zato_Audit_Log_DB_* environment variables.
    """

    def __init__(self, server_name:'str') -> 'None':

        self.server_name = server_name

        # Counts inserts so retention can run periodically instead of on every write
        self._insert_count = 0

        # All the instances in a process share one engine per configuration
        self.engine = get_audit_engine()

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
        status:'str' = '',
        duration_ms:'int' = 0,
        data:'str' = '',
        ) -> 'None':
        """ Writes one audit event, at the moment it happens, in the same process.
        """

        # The event time is always assigned here so all rows share one clock ..
        now = utcnow()
        event_time_iso = now.isoformat()

        # .. write the event ..
        insert = event_table.insert()
        insert_statement = insert.values(
            cid=cid,
            source=source,
            event_type=event_type,
            object_name=object_name,
            msg_id=msg_id,
            correl_id=correl_id,
            ext_client_id=ext_client_id,
            pub_time_iso=pub_time_iso,
            event_time_iso=event_time_iso,
            server_name=self.server_name,
            endpoint=endpoint,
            sub_key=sub_key,
            size=size,
            priority=priority,
            outcome=outcome,
            status=status,
            duration_ms=duration_ms,
            data=data,
        )

        with self.engine.begin() as connection:
            _ = connection.execute(insert_statement)

        # .. and periodically delete rows older than the retention window.
        self._insert_count += 1

        if self._insert_count % _retention_check_interval == 0:
            self._run_retention(now)

# ################################################################################################################################

    def _run_retention(self, now:'datetime') -> 'None':
        """ Deletes events older than the retention window.
        """
        retention_days = get_retention_days()

        cutoff = now - timedelta(days=retention_days)
        cutoff_iso = cutoff.isoformat()

        delete = event_table.delete()
        delete_statement = delete.where(event_table.c.event_time_iso < cutoff_iso)

        with self.engine.begin() as connection:
            result = connection.execute(delete_statement)

        if result.rowcount:
            suffix = 'event' if result.rowcount == 1 else 'events'
            logger.info('Audit log retention deleted %d %s older than %s', result.rowcount, suffix, cutoff_iso)

# ################################################################################################################################
# ################################################################################################################################
