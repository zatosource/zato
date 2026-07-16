# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rollup - reads audit log events the analytics store has not seen yet,
# aggregates them into hourly rows and advances a watermark, all in one
# analytics-side transaction. It is watermark-based and idempotent - rerunning
# from the same watermark produces the same aggregates, so overlapping cron runs
# and mid-run crashes are harmless. It runs in its own OS process, never inside
# the server - see the analytics CLI command and the make target that invoke it.

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, select, update

# Zato
from zato.common.analytics.api import get_analytics_engine, get_error_source, get_latency_bucket_index, get_status_class, \
    ErrorSource, Latency_Bucket_Count, Period_Len, usage_table, watermark_table
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    from zato.common.typing_ import anytuple, intlist

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    anytuple = anytuple
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
group_dict = dict['anytuple', '_UsageState']

# ################################################################################################################################
# ################################################################################################################################

# How many audit rows one run reads at most - the next run picks up from the new watermark
Batch_Size = 100_000

# The channel sources the rollup aggregates
_channel_sources = (AuditSource.REST_Channel, AuditSource.SOAP_Channel)

# ################################################################################################################################
# ################################################################################################################################

class RollupResult:
    """ What one rollup run did - how many events it aggregated and where the watermark is now.
    """

    def __init__(self) -> 'None':
        self.event_count:'int' = 0
        self.last_event_id:'int' = 0

# ################################################################################################################################
# ################################################################################################################################

class _UsageState:
    """ The aggregation state of one hourly row in the making.
    """

    def __init__(self) -> 'None':

        self.request_count:'int' = 0
        self.size_sum:'int' = 0
        self.duration_sum_ms:'int' = 0

        # Error counts per source
        self.error_counts:'dict[str, int]' = {
            ErrorSource.Auth:       0,
            ErrorSource.Rate_Limit: 0,
            ErrorSource.Upstream:   0,
            ErrorSource.Gateway:    0,
        }

        # One count per latency histogram bucket
        self.latency_buckets:'intlist' = [0] * Latency_Bucket_Count

# ################################################################################################################################
# ################################################################################################################################

def _load_new_events(last_event_id:'int') -> 'list':
    """ Reads the channel responses the analytics store has not aggregated yet, oldest first.
    Responses are what the rollup runs on - they carry the caller, the HTTP status
    and the request duration, while request events know none of these yet.
    """
    source_matches = event_table.c.source.in_(_channel_sources)
    event_type_matches = event_table.c.event_type == AuditEvent.Response_Sent
    newer_than_watermark = event_table.c.id > last_event_id

    conditions = and_(
        source_matches,
        event_type_matches,
        newer_than_watermark,
    )

    statement = select(
        event_table.c.id,
        event_table.c.source,
        event_table.c.object_name,
        event_table.c.ext_client_id,
        event_table.c.event_time_iso,
        event_table.c.status,
        event_table.c.duration_ms,
        event_table.c.size,
    )
    statement = statement.where(conditions)
    statement = statement.order_by(event_table.c.id)
    statement = statement.limit(Batch_Size)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.fetchall()

    return out

# ################################################################################################################################

def _aggregate_events(events:'list') -> 'group_dict':
    """ Folds the new events into per-hour aggregation states.
    """

    # Our response to produce
    out:'group_dict' = {}

    for _, source, object_name, ext_client_id, event_time_iso, status, duration_ms, size in events:

        # An event recorded by a release that did not know the status yet counts as a success
        if status is None:
            status = ''

        if duration_ms is None:
            duration_ms = 0

        # The hourly period this event belongs to
        period = event_time_iso[:Period_Len]

        status_class = get_status_class(status)

        key = (period, source, object_name, ext_client_id, status_class)

        if group := out.get(key):
            pass
        else:
            group = _UsageState()
            out[key] = group

        # Every response is one request handled ..
        group.request_count += 1
        group.size_sum += size
        group.duration_sum_ms += duration_ms

        # .. an error additionally counts against its source ..
        error_source = get_error_source(status)

        if error_source != ErrorSource.NoError:
            group.error_counts[error_source] += 1

        # .. and the duration lands in its histogram bucket.
        bucket_index = get_latency_bucket_index(duration_ms)
        group.latency_buckets[bucket_index] += 1

    return out

# ################################################################################################################################

def _upsert_group(connection:'Connection', key:'anytuple', group:'_UsageState') -> 'None':
    """ Folds one aggregation state into its hourly row, creating the row if this hour,
    channel, caller and status class have not been seen before.
    """
    period, source, channel, caller, status_class = key

    row_matches = and_(
        usage_table.c.period == period,
        usage_table.c.source == source,
        usage_table.c.channel == channel,
        usage_table.c.caller == caller,
        usage_table.c.status_class == status_class,
    )

    select_statement = select(
        usage_table.c.id,
        usage_table.c.request_count,
        usage_table.c.error_count_auth,
        usage_table.c.error_count_rate_limit,
        usage_table.c.error_count_upstream,
        usage_table.c.error_count_gateway,
        usage_table.c.size_sum,
        usage_table.c.duration_sum_ms,
        usage_table.c.latency_buckets,
    )
    select_statement = select_statement.where(row_matches)

    result = connection.execute(select_statement)
    existing = result.fetchone()

    # This hour has been seen before, so the new counts add to the stored ones ..
    if existing:

        row_id, request_count, count_auth, count_rate_limit, count_upstream, count_gateway, \
            size_sum, duration_sum_ms, latency_buckets_json = existing

        latency_buckets = loads(latency_buckets_json)

        for index in range(Latency_Bucket_Count):
            latency_buckets[index] += group.latency_buckets[index]

        update_statement = update(usage_table)
        update_statement = update_statement.where(usage_table.c.id == row_id)
        update_statement = update_statement.values(
            request_count=request_count + group.request_count,
            error_count_auth=count_auth + group.error_counts[ErrorSource.Auth],
            error_count_rate_limit=count_rate_limit + group.error_counts[ErrorSource.Rate_Limit],
            error_count_upstream=count_upstream + group.error_counts[ErrorSource.Upstream],
            error_count_gateway=count_gateway + group.error_counts[ErrorSource.Gateway],
            size_sum=size_sum + group.size_sum,
            duration_sum_ms=duration_sum_ms + group.duration_sum_ms,
            latency_buckets=dumps(latency_buckets),
        )

        _ = connection.execute(update_statement)

    # .. otherwise, a fresh row is born.
    else:
        insert_statement = usage_table.insert()
        insert_statement = insert_statement.values(
            period=period,
            source=source,
            channel=channel,
            caller=caller,
            status_class=status_class,
            request_count=group.request_count,
            error_count_auth=group.error_counts[ErrorSource.Auth],
            error_count_rate_limit=group.error_counts[ErrorSource.Rate_Limit],
            error_count_upstream=group.error_counts[ErrorSource.Upstream],
            error_count_gateway=group.error_counts[ErrorSource.Gateway],
            size_sum=group.size_sum,
            duration_sum_ms=group.duration_sum_ms,
            latency_buckets=dumps(group.latency_buckets),
        )

        _ = connection.execute(insert_statement)

# ################################################################################################################################

def _get_watermark(connection:'Connection') -> 'int':
    """ Returns the id of the last audit event already aggregated, creating and locking
    the watermark row on the way so overlapping runs serialize on it.
    """
    select_statement = select(watermark_table.c.id, watermark_table.c.last_event_id)

    result = connection.execute(select_statement)
    row = result.fetchone()

    # The very first run creates the watermark row ..
    if not row:
        insert_statement = watermark_table.insert()
        insert_statement = insert_statement.values(last_event_id=0)
        _ = connection.execute(insert_statement)

        out = 0
        return out

    row_id, last_event_id = row

    # .. later runs write it back unchanged first - the no-op update takes a write lock
    # on every database engine, so a second rollup started by an overlapping cron run
    # waits here until this one commits, then reads the already advanced watermark.
    update_statement = update(watermark_table)
    update_statement = update_statement.where(watermark_table.c.id == row_id)
    update_statement = update_statement.values(last_event_id=last_event_id)
    _ = connection.execute(update_statement)

    out = last_event_id
    return out

# ################################################################################################################################

def _advance_watermark(connection:'Connection', last_event_id:'int') -> 'None':
    """ Remembers the id of the newest audit event this run has aggregated.
    """
    update_statement = update(watermark_table)
    update_statement = update_statement.values(last_event_id=last_event_id)

    _ = connection.execute(update_statement)

# ################################################################################################################################

def run_rollup() -> 'RollupResult':
    """ One rollup run - read the audit events newer than the watermark, aggregate them
    into hourly rows, advance the watermark and exit. The aggregates and the watermark
    move in one transaction, so a crash mid-run changes nothing and the next run
    simply starts from the same place.
    """

    # Our response to produce
    out = RollupResult()

    analytics_engine = get_analytics_engine()

    with analytics_engine.begin() as connection:

        # Find out where the previous run finished ..
        last_event_id = _get_watermark(connection)

        # .. read what has been recorded since then ..
        events = _load_new_events(last_event_id)

        if not events:
            out.last_event_id = last_event_id
            return out

        # .. fold the new events into per-hour aggregation states ..
        groups = _aggregate_events(events)

        # .. land each state in its hourly row ..
        for key in sorted(groups):
            group = groups[key]
            _upsert_group(connection, key, group)

        # .. and remember how far we have come.
        newest_event = events[-1]
        newest_event_id = newest_event[0]

        _advance_watermark(connection, newest_event_id)

        out.event_count = len(events)
        out.last_event_id = newest_event_id

    suffix = 'event' if out.event_count == 1 else 'events'
    logger.info('Analytics rollup aggregated %d %s, watermark is now %d', out.event_count, suffix, out.last_event_id)

    return out

# ################################################################################################################################
# ################################################################################################################################
