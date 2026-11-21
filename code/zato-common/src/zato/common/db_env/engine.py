# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The engine factory for environment-configured databases - builds an SQLAlchemy
# engine out of a store's EnvDBConfig, creates the schema and caches the result
# so all callers in a process share one pool.

# stdlib
import fcntl
import os
from importlib import import_module
from typing import NamedTuple

# gevent
from gevent import get_hub
from gevent.monkey import get_original, is_module_patched

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Dialect, make_url
from sqlalchemy.pool import QueuePool

# Zato
from zato.common.db_env.common import get_env_values, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    DatabaseDurabilityError, PostgreSQL_Connect_Timeout_Seconds, set_postgresql_keepalive, set_postgresql_no_delay, \
    set_postgresql_read_timeout, set_postgresql_session, set_sqlite_pragmas, verify_postgresql_server
from zato.common.db_env.fence import install_fence
from zato.common.db_env.pg8000_common import Driver_Name as PG8000_Driver_Name
from zato.common.db_env.process_queue import ProcessQueue
from zato.common.db_env.sqlite_checkpoint import set_background_checkpoint_limit, WALCheckpointer
from zato.common.db_env.sqlite_stats import collect_sqlite_stats, Env_Stats_Dir
from zato.common.db_env.write_path import check_write_path, get_write_path, Mechanism, run_in_write_path, write_path
from zato.common.sqlite_connection import connect_sqlite_file as connect_sqlite_file
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

# The PostgreSQL advisory lock under which the schemas are created
_schema_lock_key = 7_401_852_117_309

# The suffix of the file beside a SQLite file, the lock of which the processes that create its schema take in turns
_schema_lock_suffix = '.schema-lock'

# Engines are cached per configuration so all callers in a process share one pool
_engine_cache:'anydict' = {}

# The background checkpointers of the cached SQLite engines that have one, by the same keys
_checkpointer_cache:'anydict' = {}

# The module whose import applies the extensions of pg8000, loaded by the first connection of pg8000 in a process
_pg8000_install_module = 'zato.common.db_env.pg8000_install'

# SQLite file engines are cached per path and pool mode
_sqlite_file_engine_cache:'anydict' = {}

# The thread locks under which the writes of this process to one SQLite file run one at a time, by the real path
# of the file. The busy timeout of SQLite does not queue its waiters, and with a hundred threads writing at once
# a single thread can wait past the timeout.
_sqlite_write_locks:'anydict' = {}

# The queues of the shared region in which the worker and the config process of one server take turns for the writes
# to one SQLite file, by the real path of the file. The thread lock of the file admits one thread of a process
# to the queue at a time, and a process that no arbiter started has no queues.
_process_queues:'anydict' = {}

# The lock of the threads of the operating system, which the threads of the gevent pool require.
_allocate_thread_lock = get_original('_thread', 'allocate_lock')

# ################################################################################################################################
# ################################################################################################################################

class _QueueBinding:
    """ The shared region of the server of a process, the place of the process in its queues, how long a write
    waits for its turn, and the queue of each SQLite file, by its real path, which is the same in both processes.
    """
    region: 'SharedRegion'
    place: 'int'
    deadline_seconds: 'float'
    queue_by_path: 'strintdict'

class _QueueState:
    binding: '_QueueBinding | None' = None

_queue_state = _QueueState()

# ################################################################################################################################
# ################################################################################################################################

class _EnvEngine(NamedTuple):
    """ An engine of an environment-configured database, the path of its file, empty for a network database,
    and whether its WAL is to be checkpointed in the background.
    """
    engine: 'Engine'
    db_path: 'str'
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

def _install_pg8000(dialect:'Dialect', connection_record:'any_', cargs:'any_', cparams:'stranydict') -> 'None':
    """ Applies the extensions of pg8000 before a connection of pg8000 is opened, whichever engine of the process opens it.
    """
    if dialect.driver == PG8000_Driver_Name:
        _ = import_module(_pg8000_install_module)

# A process whose databases are all SQLite never loads pg8000.
sa_event.listen(Dialect, 'do_connect', _install_pg8000)

# ################################################################################################################################
# ################################################################################################################################

def _new_sqlite_file_engine(
    db_path:'str',
    *,
    needs_pool:'bool',
    needs_background_checkpoint:'bool',
    ) -> '_EnvEngine':
    """ Builds an SQLAlchemy engine for a SQLite file, with the settings of its connections, and says whether its WAL
    is to be checkpointed in the background.
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

    # .. build the engine and apply the SQLite connection settings ..
    engine_url = f'sqlite:///{db_path}'
    engine = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    sa_event.listen(engine, 'connect', set_sqlite_pragmas)

    # .. the statistics of the connections are collected when the environment names a directory for them ..
    if os.environ.get(Env_Stats_Dir, ''):
        sa_event.listen(engine, 'checkin', collect_sqlite_stats)

    # .. every write runs within one of the mechanisms of the Zato database ..
    sa_event.listen(engine, 'before_cursor_execute', check_write_path)

    # .. and a file whose WAL is checkpointed in the background lets its commits append to a longer log.
    if needs_background_checkpoint:
        sa_event.listen(engine, 'connect', set_background_checkpoint_limit)

    out = _EnvEngine(engine, db_path, needs_background_checkpoint)
    return out

# ################################################################################################################################

def _create_sqlite_schema(db_path:'str', engine:'Engine', metadata_tuple:'anytuple') -> 'None':
    """ Creates the tables of a SQLite file that do not exist yet under an exclusive lock of a file beside it,
    so that processes that open a new file at the same time take turns in setting its journal mode and in creating
    its tables. Without the lock, each of them finds a table missing and creates it, and SQLite refuses the change
    of the journal mode at once, without its busy timeout, while another process holds a lock of the file.
    """
    lock_path = f'{db_path}{_schema_lock_suffix}'

    with open(lock_path, 'a') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        with write_path(Mechanism.Schema):
            for metadata in metadata_tuple:
                metadata.create_all(engine)

# ################################################################################################################################

def get_sqlite_file_engine(
    db_path:'str',
    metadata:'MetaData',
    *,
    needs_pool:'bool',
    needs_background_checkpoint:'bool',
    ) -> 'Engine':
    """ Returns an SQLAlchemy engine for a SQLite file and creates its schema if needed.
    """

    # Reuse the engine for this file and pool mode ..
    cache_key = (db_path, needs_pool)

    if engine := _sqlite_file_engine_cache.get(cache_key):
        out = engine
        return out

    # .. build the engine ..
    file_engine = _new_sqlite_file_engine(db_path, needs_pool=needs_pool,
        needs_background_checkpoint=needs_background_checkpoint)

    out = file_engine.engine

    # .. create the schema ..
    metadata_tuple = (metadata,)
    _create_sqlite_schema(db_path, out, metadata_tuple)

    # .. and retain it for subsequent callers, unless another caller retained one first.
    out = _retain_engine(_sqlite_file_engine_cache, cache_key, out, file_engine.needs_background_checkpoint, db_path)
    return out

# ################################################################################################################################

def _retain_engine(
    cache:'anydict',
    cache_key:'any_',
    engine:'Engine',
    needs_background_checkpoint:'bool',
    db_path:'str',
    ) -> 'Engine':
    """ Retains a newly built engine in its cache and returns it, or disposes of it and returns the engine
    that another caller retained under the same key while this one was being built. The schema creation
    and the start of a checkpointer yield to other greenlets under gevent, so two callers can build an engine
    for the same key, and only the first one retained is used, with a single checkpointer.
    """

    # One caller wins the key ..
    out = cache.setdefault(cache_key, engine)

    # .. and the engine of any other caller is closed ..
    if out is not engine:
        engine.dispose()
        return out

    # .. while the winner starts the checkpoints of the WAL that the commits no longer run, in one process
    # of the server, with the checkpointer retained before its thread starts, so that dispose_cached_engines
    # can stop it.
    if needs_background_checkpoint:
        if is_config_owner():
            checkpointer = WALCheckpointer(out, db_path=db_path)
            _checkpointer_cache[cache_key] = checkpointer
            checkpointer.start()

    return out

# ################################################################################################################################

def dispose_cached_engines() -> 'None':
    """ Disposes every cached engine of this process, the SQLite file engines and the environment-configured ones,
    stopping each background checkpointer, so that no checkpoint thread is left running.
    """
    for cache in (_engine_cache, _sqlite_file_engine_cache):
        cache_keys = list(cache)

        for cache_key in cache_keys:

            # The checkpoints of the engine end with it ..
            if checkpointer := _checkpointer_cache.pop(cache_key, None):
                checkpointer.stop()

            # .. and its pooled connections are closed.
            engine = cache.pop(cache_key)
            engine.dispose()

# ################################################################################################################################

def create_schemas(engine:'Engine', metadata_tuple:'anytuple') -> 'None':
    """ Creates the tables of each schema that do not exist yet. On PostgreSQL, the processes that start at the same time,
    e.g. a server and its cleanup process, create them one after another.
    """
    with write_path(Mechanism.Schema):
        if engine.dialect.name == Type_PostgreSQL:
            with engine.begin() as connection:
                _ = connection.execute(text('select pg_advisory_xact_lock(:key)'), {'key': _schema_lock_key})

                for metadata in metadata_tuple:
                    metadata.create_all(connection)
        else:
            for metadata in metadata_tuple:
                metadata.create_all(engine)

# ################################################################################################################################

def create_schema(engine:'Engine', metadata:'MetaData') -> 'None':
    """ Creates the tables of one schema that do not exist yet.
    """
    metadata_tuple = (metadata,)
    create_schemas(engine, metadata_tuple)

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
        config.env_path,
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

def _install_postgresql_settings(engine:'Engine') -> 'None':
    """ Makes each new PostgreSQL connection of an engine of Zato read its replies within a bounded time, send its segments
    without delay, detect an unreachable peer, run its session with the settings of durability and of the statement timeout,
    and refuse a server under which a commit could be acknowledged before it is durable.
    """
    sa_event.listen(engine, 'connect', set_postgresql_read_timeout)
    sa_event.listen(engine, 'connect', set_postgresql_no_delay)
    sa_event.listen(engine, 'connect', set_postgresql_keepalive)
    sa_event.listen(engine, 'connect', set_postgresql_session)
    sa_event.listen(engine, 'connect', verify_postgresql_server)

# ################################################################################################################################

def _new_env_engine(config:'EnvDBConfig') -> '_EnvEngine':
    """ Builds an SQLAlchemy engine for an environment-configured database, with the settings of its connections,
    and says whether its WAL is to be checkpointed in the background.
    """

    # Read the connection values out of the environment ..
    values  = get_env_values(config)
    db_type = values['type']

    # .. a SQLite file has an engine of its own kind ..
    if db_type == Type_SQLite:
        out = _new_sqlite_file_engine(values['name'], needs_pool=config.needs_pool,
            needs_background_checkpoint=config.needs_background_checkpoint)
        return out

    # .. while a network database is built from its URL and connection arguments ..
    engine_url   = build_engine_url_from_values(values, db_type)
    connect_args = build_connect_args_from_values(values, db_type)

    # .. a new connection to PostgreSQL is established within a bounded time ..
    if db_type == Type_PostgreSQL:
        connect_args['timeout'] = PostgreSQL_Connect_Timeout_Seconds

    # .. runs read committed, and a pooled connection that the server or a load balancer closed
    # .. in the meantime is replaced when it is checked out instead of failing the first statement sent on it ..
    engine_kwargs:'stranydict' = {}
    engine_kwargs['isolation_level'] = 'READ COMMITTED'
    engine_kwargs['pool_pre_ping'] = True

    # .. stores with many concurrent small transactions also need enough
    # .. connections for the database to group their commits into shared flushes ..
    if config.needs_pool:
        engine_kwargs['pool_size'] = values['pool_size']
        engine_kwargs['max_overflow'] = _network_max_overflow

    engine = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. every write runs within one of the mechanisms of the Zato database ..
    sa_event.listen(engine, 'before_cursor_execute', check_write_path)

    # .. PostgreSQL needs the limits and the settings of each connection ..
    if db_type == Type_PostgreSQL:
        _install_postgresql_settings(engine)

        # .. each transaction confirms that the server it runs for was not replaced by another one ..
        install_fence(engine)

        # .. a password kept in a file is read again for each new connection, which lets it be rotated ..
        if password_file := values['password_file']:
            password_reader = _PasswordFileReader(password_file)
            sa_event.listen(engine, 'do_connect', password_reader.on_connect)

        # .. pg8000 sends each row of a multi-row insert as a statement of its own, one round trip per row,
        # .. which SQLAlchemy replaces with multi-row statements only for the dialects that ask for it.
        engine.dialect.use_insertmanyvalues_wo_returning = True

    # .. and a network database checkpoints its own log.
    out = _EnvEngine(engine, '', False)
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

    # .. make sure the schemas exist ..
    if env_engine.db_path:
        _create_sqlite_schema(env_engine.db_path, out, config.metadata_tuple)
    else:
        create_schemas(out, config.metadata_tuple)

    # .. and cache the engine for all future callers, unless another caller cached one first.
    out = _retain_engine(_engine_cache, cache_key, out, env_engine.needs_background_checkpoint, env_engine.db_path)
    return out

# ################################################################################################################################

def new_unshared_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Returns an engine of an environment-configured database that no other caller receives and that runs
    no background checkpoints, which its caller disposes, e.g. the arbiter before it forks the worker and the config process.
    """
    env_engine = _new_env_engine(config)

    out = env_engine.engine
    return out

# ################################################################################################################################

def new_zato_engine(engine_url:'any_', **engine_kwargs:'any_') -> 'Engine':
    """ Returns an engine of a database of Zato that the Zato_Database_* variables do not configure, such as config.db,
    settings.db or a database of the Dashboard, with the same settings of durability on each of its connections
    as the engines of the Zato database.
    """
    db_type = make_url(engine_url).get_backend_name()

    # A new connection to PostgreSQL is established within a bounded time, with the connection arguments of the caller ..
    if db_type == Type_PostgreSQL:

        if 'connect_args' in engine_kwargs:
            connect_args = dict(engine_kwargs['connect_args'])
        else:
            connect_args = {}

        connect_args['timeout'] = PostgreSQL_Connect_Timeout_Seconds
        engine_kwargs['connect_args'] = connect_args

    out = create_engine(engine_url, **engine_kwargs)

    # .. and each connection receives the settings of its type of database.
    if db_type == Type_SQLite:
        sa_event.listen(out, 'connect', set_sqlite_pragmas)

    elif db_type == Type_PostgreSQL:
        _install_postgresql_settings(out)

    else:
        raise DatabaseDurabilityError(f'Unsupported database type `{db_type}` of a database of Zato')

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
    """ Makes the writes of this process to the SQLite file of an engine take turns with those of the other process.
    """
    write_key = _get_write_key(engine)
    _process_queues[write_key] = process_queue

# ################################################################################################################################

def get_cached_engine_count() -> 'int':
    """ Returns how many engines this process holds for its callers, none of which a process that forks may hold,
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

def bind_process_queues(region:'SharedRegion', place:'int', deadline_seconds:'float', queue_by_path:'strintdict') -> 'None':
    """ Makes the writes of this process to each SQLite file of the server take turns with those of the other process,
    in the queue of the file that the arbiter assigned before the fork.
    """
    binding = _QueueBinding()
    binding.region = region
    binding.place = place
    binding.deadline_seconds = deadline_seconds
    binding.queue_by_path = queue_by_path

    _queue_state.binding = binding

# ################################################################################################################################

def _get_write_key(engine:'Engine') -> 'str':
    """ Returns the real path of the SQLite file of an engine, under which all the engines of the file
    take turns in their writes, or the URL of a database in memory, which has no file.
    """
    if db_path := engine.url.database:
        out = os.path.realpath(db_path)
    else:
        out = str(engine.url)

    return out

# ################################################################################################################################

def _get_process_queue(write_key:'str') -> 'ProcessQueue | None':
    """ Returns the place of this process in the queue of a SQLite file, if it is bound to one.
    """
    if process_queue := _process_queues.get(write_key):
        return process_queue

    # A process that no arbiter bound writes to its files alone
    binding = _queue_state.binding

    if binding is None:
        return None

    # A file that the arbiter did not assign a queue to is written by one process only
    if write_key not in binding.queue_by_path:
        return None

    queue = binding.queue_by_path[write_key]

    out = ProcessQueue(binding.region, queue, binding.place, binding.deadline_seconds)
    _process_queues[write_key] = out

    return out

# ################################################################################################################################

def _prepare_and_run(prepare:'callable_', run:'callable_', run_args:'anytuple') -> 'any_':
    """ Runs the preparation of a database call and then the call itself, in a thread of the pool.
    """
    prepare()

    out = run(*run_args)
    return out

# ################################################################################################################################

def call_database(engine:'Engine', func:'callable_', *args:'any_', prepare:'callable_ | None'=None) -> 'any_':
    """ Runs one blocking database call, in the thread pool of the gevent hub if the engine needs it, as the work
    of the mechanism of its caller or as a serialized write if its caller runs within none. The preparation,
    if given, runs in the same thread before the call and outside of the write lock.
    """
    mechanism = get_write_path()

    if mechanism is None:
        mechanism = Mechanism.Serialized_Write

    call_args = (mechanism, func, args)

    if needs_thread_pool(engine):

        write_key = _get_write_key(engine)

        if write_key not in _sqlite_write_locks:
            _sqlite_write_locks[write_key] = _allocate_thread_lock()

        write_lock = _sqlite_write_locks[write_key]

        hub = get_hub()
        threadpool = hub.threadpool

        # The thread that waits for the turn of this process blocks in the pool, while the greenlet of the caller is suspended ..
        if process_queue := _get_process_queue(write_key):
            run = process_queue.run_under_lock
            run_args = (write_lock, run_in_write_path, call_args)
        else:
            run = _call_under_lock
            run_args = (write_lock, run_in_write_path, call_args)

        # .. and the preparation runs in that thread before it waits for the lock.
        if prepare:
            out = threadpool.apply(_prepare_and_run, (prepare, run, run_args))
        else:
            out = threadpool.apply(run, run_args)

    else:
        if prepare:
            prepare()

        out = run_in_write_path(*call_args)

    return out

# ################################################################################################################################

def read_database(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
    """ Runs one blocking read, in the thread pool of the gevent hub if the engine needs it, outside of the write lock
    of this process and of the writer queue of the server. A read of SQLite in WAL mode waits neither for a writer
    nor for the sync of a commit, so a write that waits for its sync does not delay it.
    """
    if needs_thread_pool(engine):
        hub = get_hub()
        out = hub.threadpool.apply(func, args)
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
