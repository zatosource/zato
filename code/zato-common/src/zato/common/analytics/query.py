# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The read side of the analytics store - everything the analytics screens show
# comes from these queries. They read the hourly aggregate rows only, never
# the live tables, so a year-long trend costs hundreds of rows, not millions.

# stdlib
from datetime import datetime, timedelta, timezone
from logging import getLogger
from time import perf_counter

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.analytics.api import get_analytics_engine, usage_table, Caller_Anonymous, Latency_Bucket_Count, \
    Latency_Buckets_Ms, Period_Len
from zato.common.analytics.baseline import get_anomaly_periods, period_set, Baseline_Weeks, Hours_Per_Week
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, anytuple, intlist, stranydict, strlist, strnone

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    anytuple = anytuple
    intlist = intlist
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
entity_state_dict = dict[str, '_EntityState']
period_count_dict = dict[str, int]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The selectable time windows
Range_Day     = 'day'
Range_Week    = 'week'
Range_Month   = 'month'
Range_Quarter = 'quarter'

# How far back each window reaches
Range_Hours = {
    Range_Day:     24,
    Range_Week:    7 * 24,
    Range_Month:   30 * 24,
    Range_Quarter: 90 * 24,
}

# What each window is called on the screens
Range_Label = {
    Range_Day:     'Last 24 hours',
    Range_Week:    'Last 7 days',
    Range_Month:   'Last 30 days',
    Range_Quarter: 'Last 90 days',
}

# The window a screen opens with when none was chosen
Default_Range = Range_Week

# How many channels and consumers the overview ranks
Top_Count = 10

# How many points a table sparkline has at most
_spark_max_points = 48

# The percentiles the screens show
_p50_quantile = 0.50
_p95_quantile = 0.95
_p99_quantile = 0.99

# ################################################################################################################################

# The CSV headers of each screen's table, matching the columns the screens render
Overview_CSV_Headers = ('channel', 'requests', 'errors', 'error_rate', 'p95_ms', 'consumers')
Channel_CSV_Headers  = ('consumer', 'requests', 'errors', 'error_rate', 'p95_ms', 'last_seen')
Consumer_CSV_Headers = ('channel', 'requests', 'errors', 'error_rate', 'p95_ms', 'last_seen')

# ################################################################################################################################
# ################################################################################################################################

class _EntityState:
    """ The aggregation state of one entity - a channel or a consumer - over the window.
    """

    def __init__(self) -> 'None':

        self.request_count:'int' = 0
        self.error_count:'int' = 0
        self.size_sum:'int' = 0
        self.duration_sum_ms:'int' = 0

        # One count per latency histogram bucket
        self.latency_buckets:'intlist' = [0] * Latency_Bucket_Count

        # Per-period request counts, for sparklines and timelines
        self.period_counts:'period_count_dict' = {}

        # Per-period error counts
        self.period_errors:'period_count_dict' = {}

        # The audit source of this entity's channel, for drill-down links
        self.source:'str' = ''

        # The other side of the relation - a channel counts its callers, a caller its channels
        self.related:'set[str]' = set()

        # The newest period this entity was seen in
        self.last_seen:'str' = ''

# ################################################################################################################################

    def add_row(self, period:'str', request_count:'int', error_count:'int', size_sum:'int', duration_sum_ms:'int',
        latency_buckets:'intlist') -> 'None':

        self.request_count += request_count
        self.error_count += error_count
        self.size_sum += size_sum
        self.duration_sum_ms += duration_sum_ms

        for index in range(Latency_Bucket_Count):
            self.latency_buckets[index] += latency_buckets[index]

        if period in self.period_counts:
            self.period_counts[period] += request_count
            self.period_errors[period] += error_count
        else:
            self.period_counts[period] = request_count
            self.period_errors[period] = error_count

        if period > self.last_seen:
            self.last_seen = period

# ################################################################################################################################
# ################################################################################################################################

def get_range_cutoff(now:'datetime', time_range:'str') -> 'str':
    """ Returns the hourly period the given window reaches back to.
    """
    range_hours = Range_Hours[time_range]
    cutoff = now - timedelta(hours=range_hours)

    cutoff_iso = cutoff.isoformat()

    out = cutoff_iso[:Period_Len]
    return out

# ################################################################################################################################

def period_to_ms(period:'str') -> 'int':
    """ Converts an hourly period like 2026-07-16T14 to its Unix timestamp in milliseconds.
    All periods are UTC.
    """
    when = datetime.fromisoformat(period)
    when = when.replace(tzinfo=timezone.utc)

    seconds = when.timestamp()

    out = int(seconds * 1000)
    return out

# ################################################################################################################################

def get_percentile(latency_buckets:'intlist', quantile:'float') -> 'int':
    """ Estimates a latency percentile in milliseconds out of histogram bucket counts,
    interpolating linearly inside the bucket the percentile falls into.
    """
    total = sum(latency_buckets)

    if not total:
        return 0

    target = quantile * total
    cumulative = 0

    for index, bucket_count in enumerate(latency_buckets):

        cumulative += bucket_count

        if cumulative >= target:

            # The overflow bucket has no upper boundary, so its answer is the last known one
            if index >= len(Latency_Buckets_Ms):
                out = Latency_Buckets_Ms[-1]
                return out

            upper = Latency_Buckets_Ms[index]

            if index:
                lower = Latency_Buckets_Ms[index - 1]
            else:
                lower = 0

            # How far into this bucket the percentile falls
            into_bucket = target - (cumulative - bucket_count)
            fraction = into_bucket / bucket_count

            out = int(lower + (upper - lower) * fraction)
            return out

    # Unreachable when total is positive, present so every path returns
    out = 0
    return out

# ################################################################################################################################

def _load_rows(cutoff_period:'str', channel:'str'='', caller:'strnone'=None) -> 'anylist':
    """ Reads the hourly rows of the window, optionally scoped down to one channel
    or one consumer - the anonymous consumer is stored as an empty caller,
    so the caller filter distinguishes "no filter" from "anonymous only".
    """
    conditions = [usage_table.c.period >= cutoff_period]

    if channel:
        conditions.append(usage_table.c.channel == channel)

    if caller is not None:
        conditions.append(usage_table.c.caller == caller)

    statement = select(
        usage_table.c.period,
        usage_table.c.source,
        usage_table.c.channel,
        usage_table.c.caller,
        usage_table.c.request_count,
        usage_table.c.error_count_auth,
        usage_table.c.error_count_rate_limit,
        usage_table.c.error_count_upstream,
        usage_table.c.error_count_gateway,
        usage_table.c.size_sum,
        usage_table.c.duration_sum_ms,
        usage_table.c.latency_buckets,
    )
    statement = statement.where(*conditions)
    statement = statement.order_by(usage_table.c.period)

    diag_start = perf_counter()
    engine = get_analytics_engine()
    diag_engine = perf_counter()

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = result.fetchall()

    diag_done = perf_counter()

    logger.warning('Analytics-Diag: _load_rows cutoff=%s channel=%r caller=%r -> rows=%d engine=%.1fms query=%.1fms',
        cutoff_period, channel, caller, len(out), (diag_engine - diag_start) * 1000, (diag_done - diag_engine) * 1000)

    return out

# ################################################################################################################################

def _display_caller(caller:'str') -> 'str':
    """ Returns the display name of a caller - requests that failed authentication
    have no credential by definition and aggregate under the anonymous bucket.
    """
    if caller:
        out = caller
    else:
        out = Caller_Anonymous

    return out

# ################################################################################################################################

def _build_timeline(period_counts:'period_count_dict', period_errors:'period_count_dict',
    anomalies:'period_set', cutoff_period:'str') -> 'anylist':
    """ Turns per-period counts into the flat records the main chart consumes,
    one record per period and series, with anomalous periods flagged.
    """

    # Our response to produce
    out:'anylist' = []

    for period in sorted(period_counts):

        if period < cutoff_period:
            continue

        request_count = period_counts[period]
        error_count = period_errors[period]
        ok_count = request_count - error_count

        ts_ms = period_to_ms(period)
        is_anomaly = period in anomalies

        if ok_count:
            out.append({'ts_ms': ts_ms, 'series': 'ok', 'count': ok_count, 'is_anomaly': is_anomaly})

        if error_count:
            out.append({'ts_ms': ts_ms, 'series': 'error', 'count': error_count, 'is_anomaly': is_anomaly})

    return out

# ################################################################################################################################

def get_window_periods(now:'datetime', cutoff_period:'str') -> 'strlist':
    """ Returns every hourly period of the window, from the cutoff up to now, inclusive.
    """
    now_period = now.isoformat()[:Period_Len]
    when = datetime.fromisoformat(cutoff_period)

    # Our response to produce
    out:'strlist' = []

    while True:

        period = when.isoformat()[:Period_Len]

        if period > now_period:
            break

        out.append(period)
        when = when + timedelta(hours=1)

    return out

# ################################################################################################################################

def _build_spark(period_counts:'period_count_dict', window_periods:'strlist') -> 'intlist':
    """ Turns per-period counts into a short list of sparkline points, at most
    _spark_max_points long, by summing hourly chunks of the window. Every hour
    of the window contributes a point - hours without traffic count as zero -
    so each entity's trend spans the whole window rather than only the hours
    it happened to be seen in.
    """
    period_len = len(window_periods)

    # How many hourly points one sparkline point covers
    chunk_size = 1

    if period_len > _spark_max_points:
        chunk_size = (period_len + _spark_max_points - 1) // _spark_max_points

    # Our response to produce
    out:'intlist' = []

    for start in range(0, period_len, chunk_size):

        chunk_sum = 0

        for period in window_periods[start:start + chunk_size]:
            chunk_sum += period_counts.get(period, 0)

        out.append(chunk_sum)

    return out

# ################################################################################################################################

def _fold_rows(rows:'anylist', cutoff_period:'str', group_by_channel:'bool') -> 'anytuple':
    """ Folds hourly rows into totals, a per-period series and per-entity states.
    The extended rows reaching back before the cutoff only feed the anomaly baseline.
    """
    totals = _EntityState()

    # The whole window's per-period totals also cover the baseline weeks before it
    extended_counts:'period_count_dict' = {}

    entities:'entity_state_dict' = {}

    diag_start = perf_counter()
    diag_loads_time = 0.0
    diag_loads_count = 0
    diag_skipped_count = 0

    for period, source, channel, caller, request_count, error_count_auth, error_count_rate_limit, \
        error_count_upstream, error_count_gateway, size_sum, duration_sum_ms, latency_buckets_json in rows:

        error_count = error_count_auth + error_count_rate_limit + error_count_upstream + error_count_gateway

        if period in extended_counts:
            extended_counts[period] += request_count
        else:
            extended_counts[period] = request_count

        # Rows before the cutoff only feed the baseline
        if period < cutoff_period:
            diag_skipped_count += 1
            continue

        diag_loads_start = perf_counter()
        latency_buckets = loads(latency_buckets_json)
        diag_loads_time += perf_counter() - diag_loads_start
        diag_loads_count += 1

        totals.add_row(period, request_count, error_count, size_sum, duration_sum_ms, latency_buckets)

        if group_by_channel:
            entity_name = channel
            related_name = _display_caller(caller)
        else:
            entity_name = _display_caller(caller)
            related_name = channel

        if entity := entities.get(entity_name):
            pass
        else:
            entity = _EntityState()
            entities[entity_name] = entity

        entity.add_row(period, request_count, error_count, size_sum, duration_sum_ms, latency_buckets)
        entity.source = source
        entity.related.add(related_name)

        totals.related.add(related_name)

    logger.warning('Analytics-Diag: _fold_rows rows=%d skipped_before_cutoff=%d entities=%d ' \
        'json_loads_calls=%d json_loads=%.1fms total=%.1fms',
        len(rows), diag_skipped_count, len(entities), diag_loads_count, diag_loads_time * 1000,
        (perf_counter() - diag_start) * 1000)

    out = totals, extended_counts, entities
    return out

# ################################################################################################################################

def _error_rate(request_count:'int', error_count:'int') -> 'float':
    """ Returns the percentage of requests that errored, rounded for display.
    """
    if not request_count:
        return 0.0

    out = round(100.0 * error_count / request_count, 2)
    return out

# ################################################################################################################################

def _build_totals(totals:'_EntityState') -> 'stranydict':
    """ Turns the window's aggregation state into the tile numbers of a screen.
    """
    p50 = get_percentile(totals.latency_buckets, _p50_quantile)
    p95 = get_percentile(totals.latency_buckets, _p95_quantile)
    p99 = get_percentile(totals.latency_buckets, _p99_quantile)

    out = {
        'request_count': totals.request_count,
        'error_count': totals.error_count,
        'error_rate': _error_rate(totals.request_count, totals.error_count),
        'p50_ms': p50,
        'p95_ms': p95,
        'p99_ms': p99,
        'related_count': len(totals.related),
        'last_seen': totals.last_seen,
    }

    return out

# ################################################################################################################################

def _get_anomalies(extended_counts:'period_count_dict', cutoff_period:'str') -> 'period_set':
    """ Returns which of the window's periods are anomalies against their
    hour-of-week baseline built out of the extended series.
    """
    series:'dict[str, float]' = {}
    displayed:'strlist' = []

    for period in sorted(extended_counts):

        series[period] = float(extended_counts[period])

        if period >= cutoff_period:
            displayed.append(period)

    out = get_anomaly_periods(series, displayed)
    return out

# ################################################################################################################################

def _build_entity_rows(entities:'entity_state_dict', window_periods:'strlist', top_count:'int'=0) -> 'anylist':
    """ Turns per-entity states into the table rows of a screen, ranked by traffic,
    optionally cut down to the busiest few.
    """
    def _by_traffic(name:'str') -> 'int':
        entity = entities[name]
        out = entity.request_count
        return out

    ranked = sorted(entities, key=_by_traffic, reverse=True)

    if top_count:
        ranked = ranked[:top_count]

    # Our response to produce
    out:'anylist' = []

    for name in ranked:

        entity = entities[name]

        error_rate = _error_rate(entity.request_count, entity.error_count)
        p95_ms = get_percentile(entity.latency_buckets, _p95_quantile)
        related_count = len(entity.related)
        spark = _build_spark(entity.period_counts, window_periods)

        row = {
            'name': name,
            'source': entity.source,
            'request_count': entity.request_count,
            'error_count': entity.error_count,
            'error_rate': error_rate,
            'p95_ms': p95_ms,
            'related_count': related_count,
            'last_seen': entity.last_seen,
            'spark': spark,
        }

        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_screen_data(now:'datetime', time_range:'str', channel:'str', caller:'strnone',
    group_by_channel:'bool', top_count:'int') -> 'stranydict':
    """ The one query behind every screen - loads the window plus the baseline weeks,
    folds the rows and shapes the result the way the screens and their CSVs expect.
    """
    cutoff_period = get_range_cutoff(now, time_range)
    window_periods = get_window_periods(now, cutoff_period)

    # The baseline of the anomaly marker needs earlier weeks too
    baseline_weeks_hours = Baseline_Weeks * Hours_Per_Week
    baseline_hours = Range_Hours[time_range] + baseline_weeks_hours
    baseline_cutoff = now - timedelta(hours=baseline_hours)
    baseline_cutoff_period = baseline_cutoff.isoformat()[:Period_Len]

    diag_start = perf_counter()

    rows = _load_rows(baseline_cutoff_period, channel, caller)
    diag_loaded = perf_counter()

    totals, extended_counts, entities = _fold_rows(rows, cutoff_period, group_by_channel)
    diag_folded = perf_counter()

    anomalies = _get_anomalies(extended_counts, cutoff_period)
    diag_anomalies = perf_counter()

    timeline = _build_timeline(totals.period_counts, totals.period_errors, anomalies, cutoff_period)
    diag_timeline = perf_counter()

    entity_rows = _build_entity_rows(entities, window_periods, top_count)
    diag_entity_rows = perf_counter()

    logger.warning(
        'Analytics-Diag: _get_screen_data range=%s channel=%r caller=%r group_by_channel=%s top_count=%d | ' \
        'rows=%d entities=%d timeline=%d window_periods=%d entity_rows=%d | ' \
        'load=%.1fms fold=%.1fms anomalies=%.1fms timeline=%.1fms entity_rows=%.1fms total=%.1fms',
        time_range, channel, caller, group_by_channel, top_count,
        len(rows), len(entities), len(timeline), len(window_periods), len(entity_rows),
        (diag_loaded - diag_start) * 1000,
        (diag_folded - diag_loaded) * 1000,
        (diag_anomalies - diag_folded) * 1000,
        (diag_timeline - diag_anomalies) * 1000,
        (diag_entity_rows - diag_timeline) * 1000,
        (diag_entity_rows - diag_start) * 1000)

    out = {
        'time_range': time_range,
        'cutoff_period': cutoff_period,
        'totals': _build_totals(totals),
        'timeline': timeline,
        'rows': entity_rows,
    }

    return out

# ################################################################################################################################

def get_overview(now:'datetime', time_range:'str'=Default_Range) -> 'stranydict':
    """ The overview screen - total traffic, error rate and latency percentiles,
    plus the busiest channels and consumers, each with its own trend.
    """
    channel_data = _get_screen_data(now, time_range, '', None, True, Top_Count)
    consumer_data = _get_screen_data(now, time_range, '', None, False, Top_Count)

    out = channel_data
    out['top_channels'] = channel_data.pop('rows')
    out['top_consumers'] = consumer_data['rows']

    return out

# ################################################################################################################################

def get_channel(now:'datetime', time_range:'str', channel:'str') -> 'stranydict':
    """ The per-channel screen - one channel's traffic, errors by source, latency
    and the consumers behind the numbers.
    """
    out = _get_screen_data(now, time_range, channel, None, False, 0)
    out['name'] = channel

    # Which audit source this channel's events carry, for the drill-down links
    source = ''

    for row in out['rows']:
        source = row['source']
        break

    out['source'] = source
    out['error_sources'] = get_error_sources(now, time_range, channel)

    return out

# ################################################################################################################################

def get_consumer(now:'datetime', time_range:'str', caller:'str') -> 'stranydict':
    """ The per-consumer screen - everything one credential does across all channels.
    """

    # The anonymous bucket is stored as an empty caller
    if caller == Caller_Anonymous:
        caller_filter = ''
    else:
        caller_filter = caller

    out = _get_screen_data(now, time_range, '', caller_filter, True, 0)
    out['name'] = caller

    return out

# ################################################################################################################################

def get_error_sources(now:'datetime', time_range:'str', channel:'str') -> 'stranydict':
    """ The error-source split of one channel over the window - rate limit vs auth
    vs upstream vs gateway, which is the why behind the error count.
    """
    cutoff_period = get_range_cutoff(now, time_range)

    statement = select(
        usage_table.c.error_count_auth,
        usage_table.c.error_count_rate_limit,
        usage_table.c.error_count_upstream,
        usage_table.c.error_count_gateway,
    )
    statement = statement.where(usage_table.c.period >= cutoff_period)
    statement = statement.where(usage_table.c.channel == channel)

    engine = get_analytics_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    auth = 0
    rate_limit = 0
    upstream = 0
    gateway = 0

    for count_auth, count_rate_limit, count_upstream, count_gateway in rows:
        auth += count_auth
        rate_limit += count_rate_limit
        upstream += count_upstream
        gateway += count_gateway

    out = {
        'auth': auth,
        'rate_limit': rate_limit,
        'upstream': upstream,
        'gateway': gateway,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
