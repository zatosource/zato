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
from gevent.monkey import is_module_patched

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import event as sa_event
from sqlalchemy.pool import QueuePool

# Zato
from zato.common.db_env.common import get_env_values, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    set_postgresql_no_delay, set_sqlite_pragmas
from zato.common.db_env.pg8000_copy import install as install_pg8000_copy
from zato.common.db_env.pg8000_wire import install as install_pg8000_wire
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from zato.common.db_env.common import EnvDBConfig
    from zato.common.typing_ import any_, anydict, callable_, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    any_ = any_
    callable_ = callable_
    Engine = Engine
    EnvDBConfig = EnvDBConfig
    MetaData = MetaData

# ################################################################################################################################
# ################################################################################################################################

# Pool sizing for network databases of stores that asked for a pool - every durable
# commit waits for the database's log flush and the flush is shared across all commits
# in flight, so throughput scales with how many connections may commit at once
# and SQLAlchemy's default cap of 5+10 is too low for stores like pub/sub.
# The total of 80 stays below the default connection limits of both MySQL (151)
# and PostgreSQL (100), leaving room for other clients of the same database.
_network_pool_size = 30
_network_max_overflow = 50

# Engines are cached per configuration so all callers in a process share one pool
_engine_cache:'anydict' = {}

# The connections of PostgreSQL prepare their statements once and exchange bytea values and native types in the binary format,
# and they insert rows in bulk with COPY.
install_pg8000_wire()
install_pg8000_copy()

# SQLite file engines are cached per path and pool mode
_sqlite_file_engine_cache:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_sqlite_file_engine(db_path:'str', metadata:'MetaData', *, needs_pool:'bool') -> 'Engine':
    """ Returns an SQLAlchemy engine for a SQLite file and creates its schema if needed.
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

    # .. build the engine and apply the SQLite connection settings ..
    engine_url = f'sqlite:///{db_path}'
    out = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)
    sa_event.listen(out, 'connect', set_sqlite_pragmas)

    # .. create the schema ..
    metadata.create_all(out)

    # .. and retain the engine for subsequent callers.
    _sqlite_file_engine_cache[cache_key] = out

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

    # .. all network databases run read committed so every backend behaves the same -
    # .. it is already the default of PostgreSQL, and it matters on MySQL,
    # .. whose repeatable-read default takes gap locks that deadlock concurrent
    # .. transactions deleting interleaved key ranges, e.g. pub/sub acknowledgements ..
    if db_type != Type_SQLite:
        engine_kwargs['isolation_level'] = 'READ COMMITTED'

        # .. stores with many concurrent small transactions also need enough
        # .. connections for the database to group their commits into shared flushes ..
        if config.needs_pool:
            engine_kwargs['pool_size'] = _network_pool_size
            engine_kwargs['max_overflow'] = _network_max_overflow

    out = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. SQLite needs its pragmas applied to every new connection in the pool,
    # .. and PostgreSQL needs each socket to send its segments without delay ..
    if db_type == Type_SQLite:
        sa_event.listen(out, 'connect', set_sqlite_pragmas)

    elif db_type == Type_PostgreSQL:
        sa_event.listen(out, 'connect', set_postgresql_no_delay)

        # .. pg8000 sends each row of a multi-row insert as a statement of its own, one round trip per row,
        # .. which SQLAlchemy replaces with multi-row statements only for the dialects that ask for it ..
        out.dialect.use_insertmanyvalues_wo_returning = True

    # .. make sure the schema exists - this is idempotent ..
    config.metadata.create_all(out)

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def dispose_env_engine(config:'EnvDBConfig') -> 'None':
    """ Removes this configuration's engine from the cache and closes its pooled
    connections - the next get_env_engine call builds a fresh engine.
    """
    cache_key = _get_cache_key(config)

    # An engine that was never built has nothing to close
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

def call_database(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
    """ Runs one blocking database call, in the thread pool of the gevent hub if the engine needs it.
    """
    if needs_thread_pool(engine):
        hub = get_hub()
        threadpool = hub.threadpool
        out = threadpool.apply(func, args)
    else:
        out = func(*args)

    return out

# ################################################################################################################################
# ################################################################################################################################
