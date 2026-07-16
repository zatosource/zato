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
# indefinitely at negligible size.

# SQLAlchemy
from sqlalchemy import BigInteger, Column, Index, Integer, MetaData, String, Table, Text

# Zato
from zato.common.db_env import EnvDBConfig, get_env_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The name of the SQLite file holding the analytics store
analytics_db_file_name = 'analytics.db'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Environment variables selecting and configuring the analytics store database
    Env_Type     = 'Zato_Analytics_DB_Type'
    Env_Host     = 'Zato_Analytics_DB_Host'
    Env_Port     = 'Zato_Analytics_DB_Port'
    Env_Username = 'Zato_Analytics_DB_Username'
    Env_Password = 'Zato_Analytics_DB_Password'
    Env_Name     = 'Zato_Analytics_DB_Name'

    # Environment variables configuring SSL/TLS for the analytics store database
    Env_SSL           = 'Zato_Analytics_DB_SSL'
    Env_SSL_CA_File   = 'Zato_Analytics_DB_SSL_CA_File'
    Env_SSL_Cert_File = 'Zato_Analytics_DB_SSL_Cert_File'
    Env_SSL_Key_File  = 'Zato_Analytics_DB_SSL_Key_File'
    Env_SSL_Verify    = 'Zato_Analytics_DB_SSL_Verify'

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

# ################################################################################################################################
# ################################################################################################################################

# The analytics store schema, portable across SQLite, MySQL, PostgreSQL and Oracle DB.
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

# How the analytics store database is selected and configured through the environment
_env_config = EnvDBConfig(
    env_prefix='Zato_Analytics_DB_',
    sqlite_file_name=analytics_db_file_name,
    metadata=metadata,
)

# ################################################################################################################################

def get_analytics_db_path() -> 'str':
    """ Returns the full path to the default SQLite analytics database file.
    """
    out = _env_config.get_sqlite_path()
    return out

# ################################################################################################################################

def get_analytics_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the analytics store, creating the schema if needed.
    Which database is used comes from the Zato_Analytics_DB_* environment variables,
    defaulting to a shared SQLite file.
    """
    out = get_env_engine(_env_config)
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
