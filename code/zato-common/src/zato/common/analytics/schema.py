# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import BigInteger, Column, Index, Integer, MetaData, String, Table, Text

# ################################################################################################################################
# ################################################################################################################################

# Maximum length of short string columns
_short_column_len = 255

# The schema of the analytics store in the Zato database
metadata = MetaData()

# One row per hour, channel, caller and status class
usage_table = Table('analytics_usage', metadata,
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
    Index('idx_analytics_usage_period', 'period'),
    Index('idx_analytics_usage_channel', 'channel', 'period'),
    Index('idx_analytics_usage_caller', 'caller', 'period'),
)

# The one row remembering the last audit event the rollup has already aggregated
watermark_table = Table('analytics_watermark', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('last_event_id', BigInteger),
)

# ################################################################################################################################
# ################################################################################################################################
