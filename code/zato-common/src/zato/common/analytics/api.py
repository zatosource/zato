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
# indefinitely at negligible size. The store is a set of tables in the Zato database.

# Zato
from zato.common.analytics.schema import usage_table, watermark_table
from zato.common.db_env.database import get_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine

    # Dummy assignments to satisfy type checkers
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The tables of the store, re-exported for the callers of this module
__all__ = ['usage_table', 'watermark_table']

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

# ################################################################################################################################
# ################################################################################################################################

def get_analytics_engine() -> 'Engine':
    """ Returns the SQLAlchemy engine of the Zato database, which holds the tables of the analytics store.
    """
    out = get_database_engine()
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
