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
from typing import NamedTuple

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
from zato.common.db_env.process_queue import ProcessQueue
from zato.common.db_env.sqlite_checkpoint import set_background_checkpoint_limit, WALCheckpointer
from zato.common.defaults import default_env_base_dir
from zato.common.ha.sqlite import holds_log_for_node, ReplicatedConnection, ReplicatedPragmas
from zato.common.worker_slot import is_config_owner

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from zato.common.db_env.common import EnvDBConfig
    from zato.common.typing_ import any_, anydict, anytuple, callable_, strintdict, strlist, stranydict, strtuple
    from zato_ipc_core.zato_ipc_core import SharedRegion

    # Dummy assignments to satisfy type checkers
    any_ = any_
    callable_ = callable_
    Engine = Engine
    EnvDBConfig = EnvDBConfig
    MetaData = MetaData
    SharedRegion = SharedRegion
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# All of the pooled connections of a network database are persistent, because an overflow connection is closed
# each time it is returned, and under a steady load each reconnection repeats the authentication handshake
# and the preparation of statements.
_network_max_overflow = 0

# The smallest pool that one worker process receives of a configured pool, with which the push deliveries of the worker
# still hold a connection of their share. A configured pool below it is used as it is.
Min_Worker_Pool_Size = 4

# The worker processes of the server among which the configured pool of each network database is divided,
# one in a server with one process and in every process that is not a server
_pool_worker_count = 1

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

# The queues of the shared region in which the worker processes of one server take turns for the writes to one SQLite file,
# by the URL of the file. The thread lock of the file admits one thread of a worker to the queue at a time,
# and a server with one process has no queues.
_process_queues:'anydict' = {}

# The lock of the threads of the operating system, which the threads of the gevent pool require.
_allocate_thread_lock = get_original('_thread', 'allocate_lock')

# ################################################################################################################################
# ################################################################################################################################

class _QueueBinding:
    """ The shared region of the server of a worker process, the place of the worker in its queues, how long a write
    waits for its turn, and the queue of each SQLite file, by its real path, which is the same in every worker.
    """
    region: 'SharedRegion'
    slot: 'int'
    deadline_seconds: 'float'
    queue_by_path: 'strintdict'

class _QueueState:
    binding: '_QueueBinding | None' = None

_queue_state = _QueueState()

# ################################################################################################################################
# ################################################################################################################################

class _EnvEngine(NamedTuple):
    """ An engine of an environment-configured database and whether its WAL is to be checkpointed in the background.
    """
    engine: 'Engine'
    needs_background_checkpoint: 'bool'

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

def _new_sqlite_file_engine(
    db_path:'str',
    *,
    needs_pool:'bool',
    needs_background_checkpoint:'bool',
    replicated_database:'str',
    ) -> '_EnvEngine':
    """ Builds an SQLAlchemy engine for a SQLite file, with the settings of its connections, and says whether its WAL
    is to be checkpointed in the background, which a file that the active-standby node replicates under the given name is not.
    """

    # Create the file's directory ..
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
    engine = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    if is_log_held:
        replicated_pragmas = ReplicatedPragmas(replicated_database)
        sa_event.listen(engine, 'connect', replicated_pragmas.on_connect)

    sa_event.listen(engine, 'connect', set_sqlite_pragmas)

    # .. and a file whose WAL is checkpointed in the background lets its commits append to a longer log.
    if needs_background_checkpoint:
        sa_event.listen(engine, 'connect', set_background_checkpoint_limit)

    out = _EnvEngine(engine, needs_background_checkpoint)
    return out

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

    # .. build the engine ..
    file_engine = _new_sqlite_file_engine(db_path, needs_pool=needs_pool,
        needs_background_checkpoint=needs_background_checkpoint, replicated_database=replicated_database)

    out = file_engine.engine

    # .. create the schema ..
    metadata.create_all(out)

    # .. start the checkpoints of the WAL that the commits no longer run, in one process of the server,
    # retaining the checkpointer by the engine's key so dispose_sqlite_file_engine can stop its thread ..
    if file_engine.needs_background_checkpoint:
        if is_config_owner():
            checkpointer = WALCheckpointer(out, db_path=db_path)
            checkpointer.start()
            _checkpointer_cache[cache_key] = checkpointer

    # .. and retain the engine for subsequent callers.
    _sqlite_file_engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def new_unshared_sqlite_file_engine(db_path:'str', *, replicated_database:'str') -> 'Engine':
    """ Returns an engine of a SQLite file that no other caller receives and that runs no background checkpoints,
    which its caller disposes, e.g. the arbiter before it forks the workers.
    """
    file_engine = _new_sqlite_file_engine(db_path, needs_pool=False, needs_background_checkpoint=False,
        replicated_database=replicated_database)

    out = file_engine.engine
    return out

# ################################################################################################################################

def dispose_sqlite_file_engine(db_path:'str', *, needs_pool:'bool') -> 'None':
    """ Removes this file's engine from the cache and closes its pooled connections, stopping the background
    checkpointer first - the next get_sqlite_file_engine call builds a fresh engine.
    """
    cache_key = (db_path, needs_pool)

    # The checkpoints of the engine end with it ..
    if checkpointer := _checkpointer_cache.pop(cache_key, None):
        checkpointer.stop()

    # .. and an engine that was never built has nothing to close.
    if engine := _sqlite_file_engine_cache.pop(cache_key, None):
        engine.dispose()

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

def set_pool_worker_count(worker_count:'int') -> 'None':
    """ Divides the pool of each network database that this process and the processes it forks create
    among the given number of worker processes.
    """
    global _pool_worker_count
    _pool_worker_count = worker_count

# ################################################################################################################################

def get_worker_pool_size(pool_size:'int') -> 'int':
    """ Returns the part of a configured pool size that one worker process receives, so that the workers together
    hold no more connections than configured, unless the minimum of a worker requires more.
    """
    share = pool_size // _pool_worker_count
    floor = min(pool_size, Min_Worker_Pool_Size)

    out = max(share, floor)
    return out

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

def _new_env_engine(config:'EnvDBConfig') -> '_EnvEngine':
    """ Builds an SQLAlchemy engine for an environment-configured database, with the settings of its connections,
    and says whether its WAL is to be checkpointed in the background.
    """

    # Read the connection values out of the environment ..
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

    # .. a SQLite file whose log the active-standby node holds is checkpointed by the node only,
    # .. and a network database checkpoints its own log ..
    needs_background_checkpoint = config.needs_background_checkpoint
    is_log_held = False

    if db_type == Type_SQLite:
        is_log_held = holds_log_for_node(config.replicated_database)
    else:
        needs_background_checkpoint = False

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
            engine_kwargs['pool_size'] = get_worker_pool_size(values['pool_size'])
            engine_kwargs['max_overflow'] = _network_max_overflow

    engine = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. SQLite needs its pragmas applied to every new connection in the pool,
    # .. and PostgreSQL needs each socket to send its segments without delay ..
    if db_type == Type_SQLite:

        if is_log_held:
            replicated_pragmas = ReplicatedPragmas(config.replicated_database)
            sa_event.listen(engine, 'connect', replicated_pragmas.on_connect)

        sa_event.listen(engine, 'connect', set_sqlite_pragmas)

        # .. a store whose WAL is checkpointed in the background lets its commits append to a longer log ..
        if needs_background_checkpoint:
            sa_event.listen(engine, 'connect', set_background_checkpoint_limit)

    elif db_type == Type_PostgreSQL:
        sa_event.listen(engine, 'connect', set_postgresql_no_delay)
        sa_event.listen(engine, 'connect', set_postgresql_keepalive)
        sa_event.listen(engine, 'connect', set_postgresql_session)

        # .. a password kept in a file is read again for each new connection, which lets it be rotated ..
        if password_file := values['password_file']:
            password_reader = _PasswordFileReader(password_file)
            sa_event.listen(engine, 'do_connect', password_reader.on_connect)

        # .. pg8000 sends each row of a multi-row insert as a statement of its own, one round trip per row,
        # .. which SQLAlchemy replaces with multi-row statements only for the dialects that ask for it.
        engine.dialect.use_insertmanyvalues_wo_returning = True

    out = _EnvEngine(engine, needs_background_checkpoint)
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

    # .. build the engine ..
    env_engine = _new_env_engine(config)
    out = env_engine.engine

    # .. make sure the schema exists ..
    create_schema(out, config.metadata)

    # .. start the checkpoints of the WAL that the commits no longer run, in one process of the server ..
    if env_engine.needs_background_checkpoint:
        if is_config_owner():
            checkpointer = WALCheckpointer(out)
            checkpointer.start()
            _checkpointer_cache[cache_key] = checkpointer

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def new_unshared_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Returns an engine of an environment-configured database that no other caller receives and that runs
    no background checkpoints, which its caller disposes, e.g. the arbiter before it forks the workers.
    """
    env_engine = _new_env_engine(config)

    out = env_engine.engine
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

def set_process_queue(engine:'Engine', process_queue:'ProcessQueue') -> 'None':
    """ Makes the writes of this worker process to the SQLite file of an engine take turns with those of the other workers.
    """
    url = str(engine.url)
    _process_queues[url] = process_queue

# ################################################################################################################################

def get_cached_engine_count() -> 'int':
    """ Returns how many engines this process holds for its callers, none of which a process that forks workers may hold,
    because a pooled connection inherited by several processes is used by all of them at once.
    """
    out = len(_engine_cache) + len(_sqlite_file_engine_cache)
    return out

# ################################################################################################################################

def get_queue_by_path(db_paths:'strlist') -> 'strintdict':
    """ Returns the queue of the shared region of each SQLite file of the server, by the real path of the file,
    with one queue for each file, however many stores share it.
    """
    out:'strintdict' = {}

    for db_path in db_paths:
        real_path = os.path.realpath(db_path)

        if real_path not in out:
            out[real_path] = len(out)

    return out

# ################################################################################################################################

def bind_process_queues(region:'SharedRegion', slot:'int', deadline_seconds:'float', queue_by_path:'strintdict') -> 'None':
    """ Makes the writes of this worker process to each SQLite file of the server take turns with those of the other workers,
    in the queue of the file that the arbiter assigned before the fork.
    """
    binding = _QueueBinding()
    binding.region = region
    binding.slot = slot
    binding.deadline_seconds = deadline_seconds
    binding.queue_by_path = queue_by_path

    _queue_state.binding = binding

# ################################################################################################################################

def _get_process_queue(engine:'Engine', url:'str') -> 'ProcessQueue | None':
    """ Returns the place of this worker process in the queue of the SQLite file of an engine, if it is bound to one.
    """
    if process_queue := _process_queues.get(url):
        return process_queue

    # A process that no arbiter bound writes to its files alone
    binding = _queue_state.binding

    if binding is None:
        return None

    db_path = engine.url.database

    if db_path is None:
        return None

    real_path = os.path.realpath(db_path)

    # A file that the arbiter did not assign a queue to is written by one process only
    if real_path not in binding.queue_by_path:
        return None

    queue = binding.queue_by_path[real_path]

    out = ProcessQueue(binding.region, queue, binding.slot, binding.deadline_seconds)
    _process_queues[url] = out

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

        # The thread that waits for the turn of this worker blocks in the pool, while the greenlet of the caller is suspended
        if process_queue := _get_process_queue(engine, url):
            out = threadpool.apply(process_queue.run_under_lock, (write_lock, func, args))
        else:
            out = threadpool.apply(_call_under_lock, (write_lock, func, args))
    else:
        out = func(*args)

    return out

# ################################################################################################################################

def _execute_in_transaction(engine:'Engine', statement:'any_', *params:'any_') -> 'any_':
    with engine.begin() as connection:
        out = connection.execute(statement, *params)
    return out

# ################################################################################################################################

def execute_write(engine:'Engine', statement:'any_', *params:'any_') -> 'any_':
    """ Runs one write statement in a transaction of its own, in turn with the other writes of the server to the same SQLite file.
    """
    out = call_database(engine, _execute_in_transaction, engine, statement, *params)
    return out

# ################################################################################################################################
# ################################################################################################################################
