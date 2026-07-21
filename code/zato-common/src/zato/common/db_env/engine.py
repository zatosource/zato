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

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import event as sa_event
from sqlalchemy.pool import QueuePool

# Zato
from zato.common.db_env.common import get_env_values, Type_SQLite
from zato.common.db_env.connection import build_connect_args_from_values, build_engine_url_from_values, set_sqlite_pragmas
from zato.common.db_env.schema import ensure_column_types, ensure_columns, ensure_indexes
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.db_env.common import EnvDBConfig
    from zato.common.typing_ import anydict, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    EnvDBConfig = EnvDBConfig

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

# ################################################################################################################################
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
    # .. it is already the default of PostgreSQL and Oracle DB, and it matters on MySQL,
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

    # .. SQLite needs its pragmas applied to every new connection in the pool ..
    if db_type == Type_SQLite:
        sa_event.listen(out, 'connect', set_sqlite_pragmas)

    # .. make sure the schema exists - this is idempotent ..
    config.metadata.create_all(out)

    # .. tables created by older releases may be missing newly declared columns and indexes,
    # .. and their id columns may still be 32-bit ..
    for table in config.metadata.tables.values():
        ensure_columns(out, table)
        ensure_indexes(out, table)
        ensure_column_types(out, table)

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
