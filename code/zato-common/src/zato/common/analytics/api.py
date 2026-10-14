# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Traffic analytics - the durable aggregate store behind the analytics screens.
# A standalone rollup process reads new audit log events and lands them here
# as hourly rows keyed by channel, caller and status class, each row carrying
# request counts, error counts by source, size and duration sums and latency
# histogram bucket counts. Because the aggregates are extracted before the audit
# rows expire, audit retention does not bound the trends - hourly rows are kept
# indefinitely at negligible size. The store is always a local SQLite file.

# stdlib
import os

# SQLAlchemy
from sqlalchemy import BigInteger, Column, create_engine, Index, Integer, MetaData, String, Table, Text
from sqlalchemy import event as sa_event

# Zato
from zato.common.db_env import ensure_columns, ensure_indexes
from zato.common.db_env.connection import set_sqlite_pragmas
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anydict

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding the analytics store
analytics_db_file_name = 'analytics.db'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable with the full path to the analytics store's SQLite file
    Env_Path = 'Zato_Analytics_DB_Path'

# ################################################################################################################################
# ################################################################################################################################

# Latency histogram bucket boundaries in milliseconds - the single source the Prometheus
# metrics derive their second-based boundaries from, so both views of latency agree.
Latency_Buckets_Ms = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000)

# One count per boundary plus the overflow bucket for anything above the last boundary
Latency_Bucket_Count = len(Latency_Buckets_Ms) + 1

# ################################################################################################################################

# Where an error came from, derived from the HTTP status code of the response
class ErrorSource:
    NoError    = 'none'
    Auth       = 'auth'
    Rate_Limit = 'rate_limit'
    Upstream   = 'upstream'
    Gateway    = 'gateway'

# The error sources that count as errors, in their display order
Error_Sources = (ErrorSource.Auth, ErrorSource.Rate_Limit, ErrorSource.Upstream, ErrorSource.Gateway)

# ################################################################################################################################

# What a caller that authenticated with no security definition is reported as
Caller_Anonymous = 'Anonymous'

# An ISO timestamp cut to this many characters is an hourly period, e.g. 2026-07-16T14
Period_Len = 13

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of short string columns
_short_column_len = 255

# Engines are cached per SQLite file so all callers in a process share one engine
_engine_cache:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

# The SQLite schema of the analytics store
metadata = MetaData()

# One row per hour, channel, caller and status class
usage_table = Table('usage', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('period', String(_short_column_len)),
    Column('source', String(_short_column_len)),
    Column('channel', String(_short_column_len)),
    Column('caller', String(_short_column_len)),
    Column('status_class', String(_short_column_len)),
    Column('request_count', BigInteger),
    Column('error_count_auth', BigInteger),
    Column('error_count_rate_limit', BigInteger),
    Column('error_count_upstream', BigInteger),
    Column('error_count_gateway', BigInteger),
    Column('size_sum', BigInteger),
    Column('duration_sum_ms', BigInteger),
    Column('latency_buckets', Text),
    Index('idx_usage_period', 'period'),
    Index('idx_usage_channel', 'channel', 'period'),
    Index('idx_usage_caller', 'caller', 'period'),
)

# The one row remembering the last audit event the rollup has already aggregated
watermark_table = Table('watermark', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('last_event_id', BigInteger),
)

# ################################################################################################################################
# ################################################################################################################################

def get_analytics_db_path() -> 'str':
    """ Returns the full path to the analytics store's SQLite file - the one the environment
    variable points to or, without it, the default file under the environment directory.
    """
    if out := os.environ.get(ModuleCtx.Env_Path, ''):
        pass
    else:
        out = os.path.join(default_env_base_dir, analytics_db_file_name)

    return out

# ################################################################################################################################

def get_analytics_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the analytics store's SQLite file, creating the schema if needed.
    The path is resolved on each call, so a changed environment variable selects another file at once.
    """

    # Reuse a previously built engine for the same file ..
    db_path = get_analytics_db_path()

    if engine := _engine_cache.get(db_path):
        out = engine
        return out

    # .. the file's directory may not exist yet, e.g. in freshly created environments ..
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    # .. build the engine, with the pragmas applied to each new connection ..
    out = create_engine(f'sqlite:///{db_path}')
    sa_event.listen(out, 'connect', set_sqlite_pragmas)

    # .. make sure the schema exists - this is idempotent ..
    metadata.create_all(out)

    # .. files created by older releases may be missing newly declared columns and indexes ..
    for table in metadata.tables.values():
        ensure_columns(out, table)
        ensure_indexes(out, table)

    # .. and cache the engine for all future callers.
    _engine_cache[db_path] = out

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_error_source(status:'str') -> 'str':
    """ Derives where an error came from out of the HTTP status line of a response,
    e.g. '429 Too Many Requests'. Successes have no error source.
    """
    status_code = status[:3]

    # Non-numeric statuses mean the connection itself failed, which is an upstream issue ..
    if not status_code.isdigit():
        out = ErrorSource.Upstream

    # .. the caller could not authenticate or was not authorized ..
    elif status_code in ('401', '403'):
        out = ErrorSource.Auth

    # .. the caller ran into a rate limit ..
    elif status_code == '429':
        out = ErrorSource.Rate_Limit

    # .. the backend the gateway called did not deliver ..
    elif status_code in ('502', '503', '504'):
        out = ErrorSource.Upstream

    # .. any other 4xx or 5xx is attributed to the gateway ..
    elif status_code[0] in ('4', '5'):
        out = ErrorSource.Gateway

    # .. and everything else is a success.
    else:
        out = ErrorSource.NoError

    return out

# ################################################################################################################################

def get_status_class(status:'str') -> 'str':
    """ Converts an HTTP status line to its class, e.g. '200 OK' -> '2xx'.
    """
    first_digit = status[:1]

    # Non-numeric statuses, e.g. connection failures, map to the 0xx class
    if not first_digit.isdigit():
        first_digit = '0'

    out = f'{first_digit}xx'
    return out

# ################################################################################################################################

def get_latency_bucket_index(duration_ms:'int') -> 'int':
    """ Returns the index of the histogram bucket the given duration falls into.
    """

    # The first bucket whose boundary is not exceeded is the one ..
    for index, boundary_ms in enumerate(Latency_Buckets_Ms):
        if duration_ms <= boundary_ms:
            out = index
            break

    # .. anything above the last boundary lands in the overflow bucket.
    else:
        out = Latency_Bucket_Count - 1

    return out

# ################################################################################################################################
# ################################################################################################################################
