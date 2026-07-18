# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HL7 channel dashboard's read side - hourly traffic series and per-channel
# aggregates over the audit database, plus the mapping of a channel's live state
# to its green/amber/red health. The Django views combine this with the counters
# the zato.channel.hl7.get-current-state service reports live.

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.analytics.api import Period_Len
from zato.common.analytics.query import get_range_cutoff, get_window_periods, period_to_ms, Default_Range, Range_Day, \
    Range_Hours, Range_Label, Range_Month, Range_Quarter, Range_Week
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.monitoring.health import derive_health, EndpointMetrics, HealthThresholds

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import anylist, stranydict

    anylist = anylist
    datetime = datetime
    Engine = Engine
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The range vocabulary is the analytics one, so both dashboards speak the same windows
Default_Range = Default_Range
Range_Day = Range_Day
Range_Week = Range_Week
Range_Month = Range_Month
Range_Quarter = Range_Quarter
Range_Hours = Range_Hours
Range_Label = Range_Label

# The health state of a channel whose live counters are unavailable,
# e.g. when no server responded to the state call
Health_Unknown = 'unknown'

# How many decimal places the error rate is rounded to
_error_rate_digits = 1

# ################################################################################################################################
# ################################################################################################################################

def _new_totals() -> 'stranydict':
    out = {
        'message_count': 0,
        'error_count': 0,
        'error_rate': 0.0,
        'channel_count': 0,
    }

    return out

# ################################################################################################################################

def get_channel_dashboard(engine:'Engine', now:'datetime', time_range:'str') -> 'stranydict':
    """ Returns the channel dashboard's data - the hourly ok/error timeline of the window,
    the per-channel aggregates with their sparkline series, and the window totals.
    Each message counts once, through its acknowledgment, whose outcome says
    how the message fared.
    """
    cutoff_period = get_range_cutoff(now, time_range)
    window_periods = get_window_periods(now, cutoff_period)

    period_column = func.substr(event_table.c.event_time_iso, 1, Period_Len)

    # One query carries everything - per channel, per hour, per outcome
    query = select(
        event_table.c.object_name,
        period_column,
        event_table.c.outcome,
        func.count(),
        func.max(event_table.c.event_time_iso),
    )
    query = query.where(event_table.c.source == AuditSource.HL7)
    query = query.where(event_table.c.event_type == AuditEvent.Ack_Sent)
    query = query.where(period_column >= cutoff_period)
    query = query.group_by(event_table.c.object_name, period_column, event_table.c.outcome)

    with engine.connect() as connection:
        db_rows = connection.execute(query).fetchall()

    # The timeline and the per-channel aggregates are folded out of the same rows
    timeline_counts:'stranydict' = {}
    channel_aggregates:'stranydict' = {}

    totals = _new_totals()

    for object_name, period, outcome, count, last_event_iso in db_rows:

        # Anything that is not a success is an error on the chart
        if outcome == AuditOutcome.OK:
            series = 'ok'
        else:
            series = 'error'
            totals['error_count'] += count

        totals['message_count'] += count

        # The timeline sums across channels
        timeline_key = (period, series)
        timeline_counts[timeline_key] = timeline_counts.get(timeline_key, 0) + count

        # The per-channel aggregate accumulates its own numbers
        if object_name not in channel_aggregates:
            channel_aggregates[object_name] = {
                'name': object_name,
                'received': 0,
                'errored': 0,
                'last_event_iso': '',
                'period_counts': {},
            }

        aggregate = channel_aggregates[object_name]
        aggregate['received'] += count

        if series == 'error':
            aggregate['errored'] += count

        if last_event_iso > aggregate['last_event_iso']:
            aggregate['last_event_iso'] = last_event_iso

        period_counts = aggregate['period_counts']
        period_counts[period] = period_counts.get(period, 0) + count

    # The chart records, in period order
    timeline:'anylist' = []

    for period in window_periods:
        ts_ms = period_to_ms(period)

        for series in ('ok', 'error'):
            if count := timeline_counts.get((period, series)):
                timeline.append({'ts_ms': ts_ms, 'series': series, 'count': count})

    # The per-channel rows, busiest first, each with its zero-filled sparkline
    channels:'anylist' = []

    for aggregate in sorted(channel_aggregates.values(), key=lambda item: -item['received']):

        period_counts = aggregate.pop('period_counts')
        aggregate['spark'] = [period_counts.get(period, 0) for period in window_periods]

        received = aggregate['received']
        errored = aggregate['errored']
        aggregate['error_rate'] = round(100.0 * errored / received, _error_rate_digits)

        channels.append(aggregate)

    totals['channel_count'] = len(channels)

    if totals['message_count']:
        totals['error_rate'] = round(100.0 * totals['error_count'] / totals['message_count'], _error_rate_digits)

    # Our response to produce
    out = {
        'time_range': time_range,
        'cutoff_period': cutoff_period,
        'totals': totals,
        'timeline': timeline,
        'channels': channels,
    }

    return out

# ################################################################################################################################

def derive_live_health(channel_state:'stranydict') -> 'str':
    """ Maps one channel's live state, as the get-current-state service reports it,
    to its green/amber/red health.
    """
    metrics = EndpointMetrics()
    metrics.is_connected = channel_state['is_listening']
    metrics.error_rate = channel_state['error_rate']
    metrics.silence_seconds = channel_state['silence_seconds']
    metrics.nack_streak = channel_state['nack_streak']

    out = derive_health(metrics, HealthThresholds())
    return out

# ################################################################################################################################
# ################################################################################################################################
