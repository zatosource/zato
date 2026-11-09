# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The engine factory for environment-configured databases - builds an SQLAlchemy
# engine out of a store's EnvDBConfig, creates the schema and caches the result
# so all callers in a process share one pool.

# stdlib
import os

# gevent
from gevent import get_hub
from gevent.monkey import get_original, is_module_patched

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy import event as sa_event
from sqlalchemy.pool import QueuePool

# Zato
from zato.common.db_env.common import get_env_values, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    set_postgresql_keepalive, set_postgresql_no_delay, set_postgresql_session, set_sqlite_pragmas
from zato.common.db_env.pg8000_copy import install as install_pg8000_copy
from zato.common.db_env.pg8000_wire import install as install_pg8000_wire
from zato.common.db_env.sqlite_checkpoint import set_background_checkpoint_limit, WALCheckpointer
from zato.common.defaults import default_env_base_dir
from zato.common.ha.sqlite import holds_log_for_node, ReplicatedConnection, ReplicatedPragmas

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from zato.common.db_env.common import EnvDBConfig
    from zato.common.typing_ import any_, anydict, anytuple, callable_, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    any_ = any_
    callable_ = callable_
    Engine = Engine
    EnvDBConfig = EnvDBConfig
    MetaData = MetaData

# ################################################################################################################################
# ################################################################################################################################

# All of the pooled connections of a network database are persistent, because an overflow connection is closed
# each time it is returned, and under a steady load each reconnection repeats the authentication handshake
# and the preparation of statements.
_network_max_overflow = 0

# The PostgreSQL advisory lock under which the schemas are created
_schema_lock_key = 7_401_852_117_309

# Engines are cached per configuration so all callers in a process share one pool
_engine_cache:'anydict' = {}

# The background checkpointers of the cached SQLite engines that have one, by the same keys
_checkpointer_cache:'anydict' = {}

# The connections of PostgreSQL prepare their statements once and exchange bytea values and native types in the binary format,
# and they insert rows in bulk with COPY.
install_pg8000_wire()
install_pg8000_copy()

# SQLite file engines are cached per path and pool mode
_sqlite_file_engine_cache:'anydict' = {}

# The thread locks under which the writes of this process to one SQLite file run one at a time, by the URL of the file.
# The busy timeout of SQLite does not queue its waiters, and with a hundred threads writing at once
# a single thread can wait past the timeout.
_sqlite_write_locks:'anydict' = {}

# The lock of the threads of the operating system, which the threads of the gevent pool require.
_allocate_thread_lock = get_original('_thread', 'allocate_lock')

# ################################################################################################################################
# ################################################################################################################################

class _PasswordFileReader:
    """ Supplies each new connection with the password currently stored in a file.
    """

    def __init__(self, path:'str') -> 'None':
        self.path = path

    def on_connect(self, dialect:'any_', connection_record:'any_', cargs:'any_', cparams:'stranydict') -> 'None':
        with open(self.path) as password_file:
            password = password_file.read()

        cparams['password'] = password.strip()

# ################################################################################################################################
# ################################################################################################################################

def get_sqlite_file_engine(
    db_path:'str',
    metadata:'MetaData',
    *,
    needs_pool:'bool',
    needs_background_checkpoint:'bool',
    replicated_database:'str',
    ) -> 'Engine':
    """ Returns an SQLAlchemy engine for a SQLite file and creates its schema if needed. A file that the active-standby
    node replicates under the given name is checkpointed by the node only.
    """

    # Reuse the engine for this file and pool mode ..
    cache_key = (db_path, needs_pool)

    if engine := _sqlite_file_engine_cache.get(cache_key):
        out = engine
        return out

    # .. create the file's directory ..
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    # .. configure pooling for stores with many short transactions ..
    connect_args:'stranydict' = {}
    engine_kwargs:'stranydict' = {}

    if needs_pool:
        connect_args['check_same_thread'] = False
        engine_kwargs['poolclass'] = QueuePool

    # .. a file whose log the active-standby node holds is checkpointed by the node only ..
    is_log_held = holds_log_for_node(replicated_database)

    if is_log_held:
        needs_background_checkpoint = False
        connect_args['factory'] = ReplicatedConnection

    # .. build the engine and apply the SQLite connection settings, the ones of replication first ..
    engine_url = f'sqlite:///{db_path}'
    out = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    if is_log_held:
        replicated_pragmas = ReplicatedPragmas(replicated_database)
        sa_event.listen(out, 'connect', replicated_pragmas.on_connect)

    sa_event.listen(out, 'connect', set_sqlite_pragmas)

    # .. a file whose WAL is checkpointed in the background lets its commits append to a longer log ..
    if needs_background_checkpoint:
        sa_event.listen(out, 'connect', set_background_checkpoint_limit)

    # .. create the schema ..
    metadata.create_all(out)

    # .. start the checkpoints of the WAL that the commits no longer run ..
    if needs_background_checkpoint:
        checkpointer = WALCheckpointer(out, db_path=db_path)
        checkpointer.start()

    # .. and retain the engine for subsequent callers.
    _sqlite_file_engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def create_schema(engine:'Engine', metadata:'MetaData') -> 'None':
    """ Creates the tables of a schema that do not exist yet. On PostgreSQL, the processes that start at the same time,
    e.g. a server and its cleanup process, create it one after another.
    """
    if engine.dialect.name == Type_PostgreSQL:
        with engine.begin() as connection:
            _ = connection.execute(text('select pg_advisory_xact_lock(:key)'), {'key': _schema_lock_key})
            metadata.create_all(connection)
    else:
        metadata.create_all(engine)

# ################################################################################################################################

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
        config.env_password_file,
        config.env_pool_size,
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

    # .. a SQLite file whose log the active-standby node holds is checkpointed by the node only ..
    needs_background_checkpoint = config.needs_background_checkpoint
    is_log_held = False

    if db_type == Type_SQLite:
        is_log_held = holds_log_for_node(config.replicated_database)

    if is_log_held:
        needs_background_checkpoint = False
        connect_args['factory'] = ReplicatedConnection

    # .. PostgreSQL runs read committed, and a pooled connection that the server or a load balancer closed
    # .. in the meantime is replaced when it is checked out instead of failing the first statement sent on it ..
    if db_type != Type_SQLite:
        engine_kwargs['isolation_level'] = 'READ COMMITTED'
        engine_kwargs['pool_pre_ping'] = True

        # .. stores with many concurrent small transactions also need enough
        # .. connections for the database to group their commits into shared flushes ..
        if config.needs_pool:
            engine_kwargs['pool_size'] = values['pool_size']
            engine_kwargs['max_overflow'] = _network_max_overflow

    out = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. SQLite needs its pragmas applied to every new connection in the pool,
    # .. and PostgreSQL needs each socket to send its segments without delay ..
    if db_type == Type_SQLite:

        if is_log_held:
            replicated_pragmas = ReplicatedPragmas(config.replicated_database)
            sa_event.listen(out, 'connect', replicated_pragmas.on_connect)

        sa_event.listen(out, 'connect', set_sqlite_pragmas)

        # .. a store whose WAL is checkpointed in the background lets its commits append to a longer log ..
        if needs_background_checkpoint:
            sa_event.listen(out, 'connect', set_background_checkpoint_limit)

    elif db_type == Type_PostgreSQL:
        sa_event.listen(out, 'connect', set_postgresql_no_delay)
        sa_event.listen(out, 'connect', set_postgresql_keepalive)
        sa_event.listen(out, 'connect', set_postgresql_session)

        # .. a password kept in a file is read again for each new connection, which lets it be rotated ..
        if password_file := values['password_file']:
            password_reader = _PasswordFileReader(password_file)
            sa_event.listen(out, 'do_connect', password_reader.on_connect)

        # .. pg8000 sends each row of a multi-row insert as a statement of its own, one round trip per row,
        # .. which SQLAlchemy replaces with multi-row statements only for the dialects that ask for it ..
        out.dialect.use_insertmanyvalues_wo_returning = True

    # .. make sure the schema exists ..
    create_schema(out, config.metadata)

    # .. start the checkpoints of the WAL that the commits no longer run ..
    if db_type == Type_SQLite and needs_background_checkpoint:
        checkpointer = WALCheckpointer(out)
        checkpointer.start()
        _checkpointer_cache[cache_key] = checkpointer

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def dispose_env_engine(config:'EnvDBConfig') -> 'None':
    """ Removes this configuration's engine from the cache and closes its pooled
    connections - the next get_env_engine call builds a fresh engine.
    """
    cache_key = _get_cache_key(config)

    # The checkpoints of the engine end with it ..
    if checkpointer := _checkpointer_cache.pop(cache_key, None):
        checkpointer.stop()

    # .. and an engine that was never built has nothing to close.
    if engine := _engine_cache.pop(cache_key, None):
        engine.dispose()

# ################################################################################################################################

def needs_thread_pool(engine:'Engine') -> 'bool':
    """ Says whether the database calls of an engine run in the thread pool of the gevent hub. Under gevent,
    the SQLite driver performs its calls in C without yielding to the event loop, while the drivers of the network
    databases perform their I/O through the sockets that gevent patched, each bound to the hub of its own thread.
    """
    if is_module_patched('threading'):
        out = engine.dialect.name == Type_SQLite
    else:
        out = False

    return out

# ################################################################################################################################

def _call_under_lock(lock:'any_', func:'callable_', args:'anytuple') -> 'any_':
    with lock:
        out = func(*args)
    return out

# ################################################################################################################################

def call_database(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
    """ Runs one blocking database call, in the thread pool of the gevent hub if the engine needs it.
    """
    if needs_thread_pool(engine):

        url = str(engine.url)

        if url not in _sqlite_write_locks:
            _sqlite_write_locks[url] = _allocate_thread_lock()

        write_lock = _sqlite_write_locks[url]

        hub = get_hub()
        threadpool = hub.threadpool
        out = threadpool.apply(_call_under_lock, (write_lock, func, args))
    else:
        out = func(*args)

    return out

# ################################################################################################################################
# ################################################################################################################################
