# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The engine factory for environment-configured databases - builds an SQLAlchemy
# engine out of a store's EnvDBConfig, creates the schema and caches the result
# so all callers in a process share one pool.

# stdlib
from importlib import import_module

# gevent
from gevent import get_hub

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Dialect

# Zato
from zato.common.db_env.common import get_env_values
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, \
    PostgreSQL_Connect_Timeout_Seconds, set_postgresql_keepalive, set_postgresql_no_delay, set_postgresql_read_timeout, \
    set_postgresql_session, verify_postgresql_server
from zato.common.db_env.fence import install_fence
from zato.common.db_env.pg8000_common import Driver_Name as PG8000_Driver_Name
from zato.common.db_env.write_path import check_write_path, get_write_path, Mechanism, run_in_write_path, write_path

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

# All of the pooled connections of the database are persistent, because an overflow connection is closed
# each time it is returned, and under a steady load each reconnection repeats the authentication handshake
# and the preparation of statements.
_network_max_overflow = 0

# The PostgreSQL advisory lock under which the schemas are created
_schema_lock_key = 7_401_852_117_309

# The isolation level of every transaction of the Zato database
_isolation_level = 'READ COMMITTED'

# Engines are cached per configuration so all callers in a process share one pool
_engine_cache:'anydict' = {}

# The module whose import applies the extensions of pg8000, loaded by the first connection of pg8000 in a process
_pg8000_install_module = 'zato.common.db_env.pg8000_install'

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

# A process that never connects through pg8000 never loads its extensions.
sa_event.listen(Dialect, 'do_connect', _install_pg8000)

# ################################################################################################################################
# ################################################################################################################################

def _retain_engine(cache:'anydict', cache_key:'any_', engine:'Engine') -> 'Engine':
    """ Retains a newly built engine in its cache and returns it, or disposes of it and returns the engine
    that another caller retained under the same key while this one was being built. The schema creation
    yields to other greenlets under gevent, so two callers can build an engine for the same key,
    and only the first one retained is used.
    """

    # One caller wins the key ..
    out = cache.setdefault(cache_key, engine)

    # .. and the engine of any other caller is closed.
    if out is not engine:
        engine.dispose()

    return out

# ################################################################################################################################

def dispose_cached_engines() -> 'None':
    """ Disposes every cached engine of this process.
    """
    cache_keys = list(_engine_cache)

    for cache_key in cache_keys:
        engine = _engine_cache.pop(cache_key)
        engine.dispose()

# ################################################################################################################################

def create_schemas(engine:'Engine', metadata_tuple:'anytuple') -> 'None':
    """ Creates the tables of each schema that do not exist yet. The processes that start at the same time,
    e.g. a server and its cleanup process, create them one after another.
    """
    with write_path(Mechanism.Schema):
        with engine.begin() as connection:
            _ = connection.execute(text('select pg_advisory_xact_lock(:key)'), {'key': _schema_lock_key})

            for metadata in metadata_tuple:
                metadata.create_all(connection)

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
        value = config.get_value(name)
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

def _new_engine(values:'stranydict', engine_kwargs:'stranydict') -> 'Engine':
    """ Builds an SQLAlchemy engine of the Zato database out of a dict of connection values, with the settings
    of each of its connections.
    """

    # The URL and the connection arguments come from the connection values ..
    engine_url   = build_engine_url_from_values(values)
    connect_args = build_connect_args_from_values(values)

    # .. a new connection is established within a bounded time ..
    connect_args['timeout'] = PostgreSQL_Connect_Timeout_Seconds

    # .. with the connection arguments of the caller, if it gives any ..
    if caller_connect_args := engine_kwargs.pop('connect_args', None):
        connect_args.update(caller_connect_args)

    engine = create_engine(engine_url, connect_args=connect_args, **engine_kwargs)

    # .. each connection receives the limits and the settings of durability ..
    _install_postgresql_settings(engine)

    # .. and a password kept in a file is read again for each new connection, which lets it be rotated.
    if password_file := values['password_file']:
        password_reader = _PasswordFileReader(password_file)
        sa_event.listen(engine, 'do_connect', password_reader.on_connect)

    return engine

# ################################################################################################################################

def _new_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Builds an SQLAlchemy engine for an environment-configured database, with the settings of its connections.
    """

    # Read the connection values out of the environment ..
    values = get_env_values(config)

    # .. each transaction runs read committed, and a pooled connection that the server or a load balancer closed
    # .. in the meantime is replaced when it is checked out instead of failing the first statement sent on it ..
    engine_kwargs:'stranydict' = {}
    engine_kwargs['isolation_level'] = _isolation_level
    engine_kwargs['pool_pre_ping'] = True

    # .. there are enough connections for the database to group their commits into shared flushes ..
    engine_kwargs['pool_size'] = values['pool_size']
    engine_kwargs['max_overflow'] = _network_max_overflow

    out = _new_engine(values, engine_kwargs)

    # .. every write runs within one of the mechanisms of the Zato database ..
    sa_event.listen(out, 'before_cursor_execute', check_write_path)

    # .. each transaction confirms that the server it runs for was not replaced by another one ..
    install_fence(out)

    # .. and pg8000 sends each row of a multi-row insert as a statement of its own, one round trip per row,
    # .. which SQLAlchemy replaces with multi-row statements only for the dialects that ask for it.
    out.dialect.use_insertmanyvalues_wo_returning = True

    return out

# ################################################################################################################################

def get_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Returns an SQLAlchemy engine for an environment-configured database, creating the schema if needed.
    Which database is used comes from the environment variables named after this store's prefix.
    """

    # Reuse a previously built engine if the configuration has not changed ..
    cache_key = _get_cache_key(config)

    if engine := _engine_cache.get(cache_key):
        out = engine
        return out

    # .. build the engine ..
    out = _new_env_engine(config)

    # .. make sure the schemas exist ..
    create_schemas(out, config.metadata_tuple)

    # .. and cache the engine for all future callers, unless another caller cached one first.
    out = _retain_engine(_engine_cache, cache_key, out)
    return out

# ################################################################################################################################

def new_unshared_env_engine(config:'EnvDBConfig') -> 'Engine':
    """ Returns an engine of an environment-configured database that no other caller receives, which its caller disposes,
    e.g. the arbiter before it forks the worker and the config process.
    """
    out = _new_env_engine(config)
    return out

# ################################################################################################################################

def new_env_odb_engine(config:'EnvDBConfig', **engine_kwargs:'any_') -> 'Engine':
    """ Returns an engine of the tables of the configuration database and of Dashboard, which reside in the database
    of an environment-configured store, with the same settings of durability on each of its connections
    as the engines of that store. Its writes are not subject to the mechanisms of the Zato database.
    """
    values = get_env_values(config)

    out = _new_engine(values, engine_kwargs)
    return out

# ################################################################################################################################

def dispose_env_engine(config:'EnvDBConfig') -> 'None':
    """ Removes this configuration's engine from the cache and closes its pooled
    connections - the next get_env_engine call builds a fresh engine.
    """
    cache_key = _get_cache_key(config)

    # An engine that was never built has nothing to close.
    if engine := _engine_cache.pop(cache_key, None):
        engine.dispose()

# ################################################################################################################################

def get_cached_engine_count() -> 'int':
    """ Returns how many engines this process holds for its callers, none of which a process that forks may hold,
    because a pooled connection inherited by several processes is used by all of them at once.
    """
    out = len(_engine_cache)
    return out

# ################################################################################################################################

def call_database(engine:'Engine', func:'callable_', *args:'any_', prepare:'callable_ | None'=None) -> 'any_':
    """ Runs one blocking database call as the work of the mechanism of its caller or as a serialized write
    if its caller runs within none. The preparation, if given, runs before the call.
    """
    mechanism = get_write_path()

    if mechanism is None:
        mechanism = Mechanism.Serialized_Write

    # The preparation runs in the thread pool of the gevent hub, because it digests and indexes payloads
    # without the GIL, which would otherwise hold up every greenlet of the hub for as long as it runs.
    if prepare:
        hub = get_hub()
        _ = hub.threadpool.apply(prepare)

    out = run_in_write_path(mechanism, func, args)
    return out

# ################################################################################################################################

def _execute_in_transaction(engine:'Engine', statement:'any_', *params:'any_') -> 'any_':
    with engine.begin() as connection:
        out = connection.execute(statement, *params)
    return out

# ################################################################################################################################

def execute_write(engine:'Engine', statement:'any_', *params:'any_') -> 'any_':
    """ Runs one write statement in a transaction of its own.
    """
    out = call_database(engine, _execute_in_transaction, engine, statement, *params)
    return out

# ################################################################################################################################
# ################################################################################################################################
