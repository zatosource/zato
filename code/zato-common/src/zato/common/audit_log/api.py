# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import ssl
from datetime import timedelta
from logging import getLogger

# SQLAlchemy
from sqlalchemy import Column, create_engine, Index, Integer, MetaData, String, Table, Text
from sqlalchemy import event as sa_event

# Zato
from zato.common.defaults import default_env_base_dir
from zato.common.util.api import as_bool, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from ssl import SSLContext
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    datetime = datetime
    Engine = Engine
    SSLContext = SSLContext

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

    # Recognized database types
    Type_SQLite     = 'sqlite'
    Type_MySQL      = 'mysql'
    Type_PostgreSQL = 'postgresql'
    Type_Oracle     = 'oracle'

    # What is used when Zato_Audit_Log_DB_Type is not set
    Default_Type = Type_SQLite

    # SSL is off unless requested explicitly
    Default_SSL = False

    # When SSL is on, the server certificate is verified unless turned off explicitly
    Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

# SQLAlchemy dialects for each database type
_dialects = {
    ModuleCtx.Type_MySQL:      'mysql+pymysql',
    ModuleCtx.Type_PostgreSQL: 'postgresql+pg8000',
    ModuleCtx.Type_Oracle:     'oracle+oracledb',
}

# Default ports for each database type
_default_ports = {
    ModuleCtx.Type_MySQL:      3306,
    ModuleCtx.Type_PostgreSQL: 5432,
    ModuleCtx.Type_Oracle:     1521,
}

# How many days of events are kept - also the widest window the reports run over
Retention_Days = 30

# Retention runs after every that many inserts
_retention_check_interval = 1000

# Maximum length of short string columns
_short_column_len = 255

# Maximum length of the endpoint column - it may hold full addresses
_endpoint_column_len = 500

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
    Column('data', Text),
    Index('idx_event_source_object', 'source', 'object_name', 'id'),
    Index('idx_event_cid', 'cid', 'id'),
)

# ################################################################################################################################
# ################################################################################################################################

def get_audit_db_path() -> 'str':
    """ Returns the full path to the default SQLite audit database file.
    """
    out = os.path.join(default_env_base_dir, audit_db_file_name)
    return out

# ################################################################################################################################

def _set_sqlite_pragmas(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ WAL mode lets multiple server processes and the web-admin reader share the file safely,
    and synchronous=NORMAL keeps each insert fast while remaining durable enough for audit data.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute('pragma journal_mode=wal')
    _ = cursor.execute('pragma synchronous=normal')
    cursor.close()

# ################################################################################################################################

def _build_ssl_context() -> 'SSLContext':
    """ Builds an SSL context out of the Zato_Audit_Log_DB_SSL_* environment variables.
    """
    ca_file   = os.environ.get(ModuleCtx.Env_SSL_CA_File, '')
    cert_file = os.environ.get(ModuleCtx.Env_SSL_Cert_File, '')
    key_file  = os.environ.get(ModuleCtx.Env_SSL_Key_File, '')

    # The server certificate is verified by default when SSL is on ..
    if verify := os.environ.get(ModuleCtx.Env_SSL_Verify, ''):
        needs_verify = as_bool(verify)
    else:
        needs_verify = ModuleCtx.Default_SSL_Verify

    # .. verify against the given CA or, if none was given, against the system store ..
    if ca_file:
        out = ssl.create_default_context(cafile=ca_file)
    else:
        out = ssl.create_default_context()

    # .. a client certificate is only needed for mutual TLS ..
    if cert_file:
        out.load_cert_chain(cert_file, key_file)

    # .. and verification can be turned off explicitly.
    if not needs_verify:
        out.check_hostname = False
        out.verify_mode = ssl.CERT_NONE

    return out

# ################################################################################################################################

def _get_connect_args(db_type:'str') -> 'stranydict':
    """ Returns driver-specific connection arguments, including SSL ones if SSL is enabled.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL never applies to SQLite files ..
    if db_type == ModuleCtx.Type_SQLite:
        return out

    # .. it is off unless requested explicitly ..
    if ssl_enabled := os.environ.get(ModuleCtx.Env_SSL, ''):
        needs_ssl = as_bool(ssl_enabled)
    else:
        needs_ssl = ModuleCtx.Default_SSL

    if not needs_ssl:
        return out

    # .. each driver receives the same SSL context under its own keyword ..
    ssl_context = _build_ssl_context()

    # .. PyMySQL accepts an SSL context directly ..
    if db_type == ModuleCtx.Type_MySQL:
        out['ssl'] = ssl_context

    # .. so does pg8000 ..
    elif db_type == ModuleCtx.Type_PostgreSQL:
        out['ssl'] = ssl_context

    # .. and Oracle DB additionally needs the TCPS protocol.
    else:
        out['protocol'] = 'tcps'
        out['ssl_context'] = ssl_context

    return out

# ################################################################################################################################

def _get_engine_url(db_type:'str') -> 'str':
    """ Builds the SQLAlchemy URL for the audit log database out of environment variables.
    """

    # SQLite needs a file path only, defaulting to the shared audit database file ..
    if db_type == ModuleCtx.Type_SQLite:

        if db_path := os.environ.get(ModuleCtx.Env_Name, ''):
            pass
        else:
            db_path = get_audit_db_path()

        out = f'sqlite:///{db_path}'
        return out

    # .. everything else is a network database with full credentials.
    dialect  = _dialects[db_type]
    host     = os.environ[ModuleCtx.Env_Host]
    username = os.environ[ModuleCtx.Env_Username]
    password = os.environ[ModuleCtx.Env_Password]
    db_name  = os.environ[ModuleCtx.Env_Name]

    if port := os.environ.get(ModuleCtx.Env_Port, ''):
        port = int(port)
    else:
        port = _default_ports[db_type]

    out = f'{dialect}://{username}:{password}@{host}:{port}/{db_name}'
    return out

# ################################################################################################################################

# Engines are cached per configuration so all AuditLog instances in a process share one pool
_engine_cache:'anydict' = {}

def _get_cache_key() -> 'strtuple':
    """ Returns a cache key covering all the environment variables that influence the engine.
    """
    values = []

    for name in (
        ModuleCtx.Env_Type,
        ModuleCtx.Env_Host,
        ModuleCtx.Env_Port,
        ModuleCtx.Env_Username,
        ModuleCtx.Env_Password,
        ModuleCtx.Env_Name,
        ModuleCtx.Env_SSL,
        ModuleCtx.Env_SSL_CA_File,
        ModuleCtx.Env_SSL_Cert_File,
        ModuleCtx.Env_SSL_Key_File,
        ModuleCtx.Env_SSL_Verify,
    ):
        value = os.environ.get(name, '')
        values.append(value)

    out = tuple(values)
    return out

# ################################################################################################################################

def get_audit_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the audit log database, creating the schema if needed.
    Which database is used comes from the Zato_Audit_Log_DB_* environment variables,
    defaulting to a shared SQLite file.
    """

    # Reuse a previously built engine if the configuration has not changed ..
    cache_key = _get_cache_key()

    if engine := _engine_cache.get(cache_key):
        out = engine
        return out

    # .. find out which database type we are to use ..
    if db_type := os.environ.get(ModuleCtx.Env_Type, ''):
        pass
    else:
        db_type = ModuleCtx.Default_Type

    # .. the environment directory may not exist yet, e.g. in freshly created environments ..
    if db_type == ModuleCtx.Type_SQLite:
        os.makedirs(default_env_base_dir, exist_ok=True)

    # .. build the engine itself ..
    engine_url   = _get_engine_url(db_type)
    connect_args = _get_connect_args(db_type)
    out          = create_engine(engine_url, connect_args=connect_args)

    # .. SQLite needs its pragmas applied to every new connection in the pool ..
    if db_type == ModuleCtx.Type_SQLite:
        sa_event.listen(out, 'connect', _set_sqlite_pragmas)

    # .. make sure the schema exists - this is idempotent ..
    metadata.create_all(out)

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

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
        cutoff = now - timedelta(days=Retention_Days)
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
