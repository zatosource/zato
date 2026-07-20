# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Environment-configured SQLAlchemy engines - the audit log and the analytics store
# both live in their own database selected through a family of environment variables,
# e.g. Zato_Audit_Log_DB_* or Zato_Analytics_DB_*, defaulting to an SQLite file.
# This module builds and caches such engines so each store only declares its
# environment prefix, its default SQLite file name and its schema.

# stdlib
import os
import ssl
from logging import getLogger

# SQLAlchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy import event as sa_event
from sqlalchemy import text as sa_text
from sqlalchemy.pool import QueuePool

# Zato
from zato.common.defaults import default_env_base_dir
from zato.common.util.api import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ssl import SSLContext
    from sqlalchemy import MetaData, Table
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, anydict, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    MetaData = MetaData
    SSLContext = SSLContext
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Recognized database types
Type_SQLite     = 'sqlite'
Type_MySQL      = 'mysql'
Type_PostgreSQL = 'postgresql'
Type_Oracle     = 'oracle'

# What is used when the type variable is not set
Default_Type = Type_SQLite

# SSL is off unless requested explicitly
Default_SSL = False

# When SSL is on, the server certificate is verified unless turned off explicitly
Default_SSL_Verify = True

# ################################################################################################################################
# ################################################################################################################################

# SQLAlchemy dialects for each database type
_dialects = {
    Type_MySQL:      'mysql+pymysql',
    Type_PostgreSQL: 'postgresql+pg8000',
    Type_Oracle:     'oracle+oracledb',
}

# Default ports for each database type
_default_ports = {
    Type_MySQL:      3306,
    Type_PostgreSQL: 5432,
    Type_Oracle:     1521,
}

# ################################################################################################################################
# ################################################################################################################################

class EnvDBConfig:
    """ Describes one environment-configured database - the environment variables
    selecting it, its default SQLite file name and the schema it needs.
    """

    def __init__(self, *, env_prefix:'str', sqlite_file_name:'str', metadata:'MetaData', needs_pool:'bool'=False) -> 'None':

        self.env_prefix = env_prefix
        self.sqlite_file_name = sqlite_file_name
        self.metadata = metadata

        # Whether SQLite connections are pooled - SQLAlchemy's default for file-based SQLite
        # is no pooling at all, which makes every transaction open and close the database file,
        # and each close checkpoints the WAL, costing more than ten milliseconds. Stores with
        # many small transactions, such as pub/sub, need a real pool instead.
        self.needs_pool = needs_pool

        # The full names of the environment variables selecting and configuring the database
        self.env_type     = f'{env_prefix}Type'
        self.env_host     = f'{env_prefix}Host'
        self.env_port     = f'{env_prefix}Port'
        self.env_username = f'{env_prefix}Username'
        self.env_password = f'{env_prefix}Password'
        self.env_name     = f'{env_prefix}Name'

        # The full names of the environment variables configuring SSL/TLS
        self.env_ssl           = f'{env_prefix}SSL'
        self.env_ssl_ca_file   = f'{env_prefix}SSL_CA_File'
        self.env_ssl_cert_file = f'{env_prefix}SSL_Cert_File'
        self.env_ssl_key_file  = f'{env_prefix}SSL_Key_File'
        self.env_ssl_verify    = f'{env_prefix}SSL_Verify'

# ################################################################################################################################

    def get_sqlite_path(self) -> 'str':
        """ Returns the full path to the default SQLite file of this database.
        """
        out = os.path.join(default_env_base_dir, self.sqlite_file_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

# How long an SQLite write waits for another writer to finish before giving up,
# in milliseconds - without this, two processes sharing one file, e.g. a server
# and the cron-driven cleanup process, fail immediately with a locked-database
# error instead of taking turns. Writes are bounded batches, so the wait is short.
_sqlite_busy_timeout_ms = 5000

def _set_sqlite_pragmas(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ WAL mode lets multiple processes share the file safely, synchronous=NORMAL
    keeps each insert fast while remaining durable enough for aggregate and audit data,
    and the busy timeout makes concurrent writers from separate processes take turns.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute('pragma journal_mode=wal')
    _ = cursor.execute('pragma synchronous=normal')
    _ = cursor.execute(f'pragma busy_timeout={_sqlite_busy_timeout_ms}')
    cursor.close()

# ################################################################################################################################

def build_ssl_context_from_values(values:'stranydict') -> 'SSLContext':
    """ Builds an SSL context out of a dict of connection values.
    """
    ca_file      = values['ssl_ca_file']
    cert_file    = values['ssl_cert_file']
    key_file     = values['ssl_key_file']
    needs_verify = values['ssl_verify']

    # Verify against the given CA or, if none was given, against the system store ..
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

def build_connect_args_from_values(values:'stranydict', db_type:'str') -> 'stranydict':
    """ Returns driver-specific connection arguments, including SSL ones if SSL is enabled,
    all built out of a dict of connection values.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL never applies to SQLite files ..
    if db_type == Type_SQLite:
        return out

    # .. it is off unless requested explicitly ..
    if not values['ssl']:
        return out

    # .. each driver receives the same SSL context under its own keyword ..
    ssl_context = build_ssl_context_from_values(values)

    # .. PyMySQL accepts an SSL context directly ..
    if db_type == Type_MySQL:
        out['ssl'] = ssl_context

    # .. so does pg8000 ..
    elif db_type == Type_PostgreSQL:
        out['ssl'] = ssl_context

    # .. and Oracle DB additionally needs the TCPS protocol.
    else:
        out['protocol'] = 'tcps'
        out['ssl_context'] = ssl_context

    return out

# ################################################################################################################################

def build_engine_url_from_values(values:'stranydict', db_type:'str') -> 'str':
    """ Builds the SQLAlchemy URL for a database out of a dict of connection values.
    """

    # SQLite needs a file path only ..
    if db_type == Type_SQLite:
        db_path = values['name']
        out = f'sqlite:///{db_path}'
        return out

    # .. everything else is a network database with full credentials.
    dialect  = _dialects[db_type]
    host     = values['host']
    username = values['username']
    password = values['password']
    db_name  = values['name']

    if port := values['port']:
        port = int(port)
    else:
        port = _default_ports[db_type]

    out = f'{dialect}://{username}:{password}@{host}:{port}/{db_name}'
    return out

# ################################################################################################################################

def get_env_values(config:'EnvDBConfig') -> 'stranydict':
    """ Reads this database's environment variables into a dict of connection values,
    filling in the defaults for anything that is not set.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The type has a well-known default ..
    if db_type := os.environ.get(config.env_type, ''):
        out['type'] = db_type
    else:
        out['type'] = Default_Type

    # .. the SQLite file path defaults to this store's shared file ..
    if name := os.environ.get(config.env_name, ''):
        out['name'] = name
    elif out['type'] == Type_SQLite:
        out['name'] = config.get_sqlite_path()
    else:
        out['name'] = ''

    # .. the network location and credentials are empty unless given ..
    out['host']     = os.environ.get(config.env_host, '')
    out['port']     = os.environ.get(config.env_port, '')
    out['username'] = os.environ.get(config.env_username, '')
    out['password'] = os.environ.get(config.env_password, '')

    # .. SSL is off unless requested explicitly ..
    if ssl_enabled := os.environ.get(config.env_ssl, ''):
        out['ssl'] = as_bool(ssl_enabled)
    else:
        out['ssl'] = Default_SSL

    # .. the server certificate is verified by default when SSL is on ..
    if verify := os.environ.get(config.env_ssl_verify, ''):
        out['ssl_verify'] = as_bool(verify)
    else:
        out['ssl_verify'] = Default_SSL_Verify

    # .. and the certificate paths are empty unless given.
    out['ssl_ca_file']   = os.environ.get(config.env_ssl_ca_file, '')
    out['ssl_cert_file'] = os.environ.get(config.env_ssl_cert_file, '')
    out['ssl_key_file']  = os.environ.get(config.env_ssl_key_file, '')

    return out

# ################################################################################################################################

# Engines are cached per configuration so all callers in a process share one pool
_engine_cache:'anydict' = {}

def _get_cache_key(config:'EnvDBConfig') -> 'strtuple':
    """ Returns a cache key covering all the environment variables that influence the engine.
    """
    values = [config.env_prefix]

    for name in (
        config.env_type,
        config.env_host,
        config.env_port,
        config.env_username,
        config.env_password,
        config.env_name,
        config.env_ssl,
        config.env_ssl_ca_file,
        config.env_ssl_cert_file,
        config.env_ssl_key_file,
        config.env_ssl_verify,
    ):
        value = os.environ.get(name, '')
        values.append(value)

    out = tuple(values)
    return out

# ################################################################################################################################

def ensure_columns(engine:'Engine', table:'Table') -> 'None':
    """ Adds to an existing table any columns its declaration has gained since the table
    was first created - new columns arrive with new releases and the databases created
    by older ones need to learn about them.
    """
    inspector = inspect(engine)
    existing = inspector.get_columns(table.name)

    # The names the database already knows about
    existing_names = set()

    for column_info in existing:
        existing_names.add(column_info['name'])

    # Oracle DB is the one dialect that does not accept the COLUMN keyword here
    if engine.dialect.name == Type_Oracle:
        add_clause = 'ADD'
    else:
        add_clause = 'ADD COLUMN'

    for column in table.columns:

        if column.name in existing_names:
            continue

        # Let the dialect render the correct type name for this column
        type_sql = column.type.compile(engine.dialect)
        ddl = f'ALTER TABLE {table.name} {add_clause} {column.name} {type_sql}'

        with engine.begin() as connection:
            _ = connection.execute(sa_text(ddl))

        logger.info('Added column `%s` to table `%s`', column.name, table.name)

# ################################################################################################################################

def ensure_indexes(engine:'Engine', table:'Table') -> 'None':
    """ Creates on an existing table any indexes its declaration has gained since the table
    was first created - create_all only builds indexes together with new tables,
    so databases created by older releases need to learn about new ones here.
    """
    inspector = inspect(engine)
    existing = inspector.get_indexes(table.name)

    # The names the database already knows about
    existing_names = set()

    for index_info in existing:
        existing_names.add(index_info['name'])

    for index in table.indexes:

        if index.name in existing_names:
            continue

        index.create(engine)

        logger.info('Added index `%s` to table `%s`', index.name, table.name)

# ################################################################################################################################

def get_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Returns an SQLAlchemy engine for an environment-configured database,
    creating the schema if needed. Which database is used comes from the
    environment variables named after this store's prefix, defaulting
    to a shared SQLite file.
    """

    # Reuse a previously built engine if the configuration has not changed ..
    cache_key = _get_cache_key(config)

    if engine := _engine_cache.get(cache_key):
        out = engine
        return out

    # .. read the connection values out of the environment ..
    values  = get_env_values(config)
    db_type = values['type']

    # .. the environment directory may not exist yet, e.g. in freshly created environments ..
    if db_type == Type_SQLite:
        os.makedirs(default_env_base_dir, exist_ok=True)

    # .. build the engine itself ..
    engine_url   = build_engine_url_from_values(values, db_type)
    connect_args = build_connect_args_from_values(values, db_type)

    # .. network databases are pooled by default but file-based SQLite is not,
    # .. so stores that asked for a pool receive one - the pool hands each connection
    # .. to one user at a time, which is what the same-thread check is relaxed for ..
    engine_kwargs:'stranydict' = {}

    if db_type == Type_SQLite and config.needs_pool:
        engine_kwargs['poolclass'] = QueuePool
        connect_args['check_same_thread'] = False

    out = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. SQLite needs its pragmas applied to every new connection in the pool ..
    if db_type == Type_SQLite:
        sa_event.listen(out, 'connect', _set_sqlite_pragmas)

    # .. make sure the schema exists - this is idempotent ..
    config.metadata.create_all(out)

    # .. tables created by older releases may be missing newly declared columns and indexes ..
    for table in config.metadata.tables.values():
        ensure_columns(out, table)
        ensure_indexes(out, table)

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
