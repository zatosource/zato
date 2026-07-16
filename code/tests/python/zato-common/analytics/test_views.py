# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone

# Zato
from live_sql.env import database_env
from zato.common.analytics.api import get_analytics_engine, usage_table, Caller_Anonymous, Latency_Bucket_Count
from zato.common.analytics.csv_export import channel_csv, consumer_csv, overview_csv
from zato.common.analytics.query import get_channel, get_consumer, get_overview, period_to_ms, Range_Day
from zato.common.audit_log.api import AuditSource, ModuleCtx as AuditLogCtx
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

    # Dummy assignments to satisfy type checkers
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The moment all the queries below run at, so the seeded periods are always inside the window
_now = datetime(2026, 7, 16, 12, 0, tzinfo=timezone.utc)

# Hourly periods inside the last-24-hours window of _now
_period_ten    = '2026-07-16T10'
_period_eleven = '2026-07-16T11'

# An hourly period a few days before the window, feeding the baseline only
_period_old = '2026-07-10T10'

# The channels and callers of the seeded rows
_channel_a = 'analytics.views.channel.a'
_channel_b = 'analytics.views.channel.b'

_caller_alice = 'analytics.views.alice'
_caller_bob   = 'analytics.views.bob'

# Which histogram bucket all the seeded requests land in - its boundaries are 50 and 100 ms,
# so the p95 of any all-in-this-bucket histogram interpolates to 50 + 50 * 0.95 = 97.
_seed_bucket_index = 4
_expected_p95_ms = 97

# ################################################################################################################################
# ################################################################################################################################

def _seed_buckets(request_count:'int') -> 'intlist':
    """ A latency histogram with all the requests in one known bucket.
    """

    # Our response to produce
    out:'intlist' = [0] * Latency_Bucket_Count
    out[_seed_bucket_index] = request_count

    return out

# ################################################################################################################################

def _insert_usage_row(
    *,
    period:'str',
    channel:'str',
    caller:'str',
    status_class:'str',
    request_count:'int',
    error_count_auth:'int'=0,
    error_count_rate_limit:'int'=0,
) -> 'None':
    """ Seeds one hourly row the way the rollup would have written it.
    """
    size_sum = request_count * 10
    duration_sum_ms = request_count * 75

    latency_buckets = _seed_buckets(request_count)
    latency_buckets_json = dumps(latency_buckets)

    insert_statement = usage_table.insert().values(
        period=period,
        source=AuditSource.REST_Channel,
        channel=channel,
        caller=caller,
        status_class=status_class,
        request_count=request_count,
        error_count_auth=error_count_auth,
        error_count_rate_limit=error_count_rate_limit,
        error_count_upstream=0,
        error_count_gateway=0,
        size_sum=size_sum,
        duration_sum_ms=duration_sum_ms,
        latency_buckets=latency_buckets_json,
    )

    engine = get_analytics_engine()

    with engine.begin() as connection:
        _ = connection.execute(insert_statement)

# ################################################################################################################################

def _seed_store() -> 'None':
    """ A small store with two channels, two callers, an anonymous bucket, auth
    and rate-limit errors and one row old enough to sit outside the window.
    """

    # One caller's successes and auth failures on one channel in one hour ..
    _insert_usage_row(period=_period_ten, channel=_channel_a, caller=_caller_alice, status_class='2xx', request_count=100)
    _insert_usage_row(period=_period_ten, channel=_channel_a, caller=_caller_alice, status_class='4xx', request_count=10,
        error_count_auth=10)

    # .. another caller on both channels in the next hour ..
    _insert_usage_row(period=_period_eleven, channel=_channel_b, caller=_caller_bob, status_class='2xx', request_count=50)
    _insert_usage_row(period=_period_eleven, channel=_channel_a, caller=_caller_bob, status_class='2xx', request_count=20)

    # .. rate-limited requests that never authenticated, under the anonymous caller ..
    _insert_usage_row(period=_period_eleven, channel=_channel_a, caller='', status_class='4xx', request_count=5,
        error_count_rate_limit=5)

    # .. and one row outside the day window, which only the baseline may see.
    _insert_usage_row(period=_period_old, channel=_channel_a, caller=_caller_alice, status_class='2xx', request_count=999)

# ################################################################################################################################
# ################################################################################################################################

def test_analytics_views(tmp_path:'os.PathLike') -> 'None':
    """ The read side of the analytics store - rankings, trends, the consumer page,
    the anonymous bucket and the CSV renderers, all over one seeded store.
    """
    db_path = os.path.join(str(tmp_path), 'analytics.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env('Zato_Analytics_DB_', details):

        _seed_store()

        # The overview counts the window and only the window ..
        overview = get_overview(_now, Range_Day)
        totals = overview['totals']

        assert totals['request_count'] == 185
        assert totals['error_count'] == 15
        assert totals['error_rate'] == 8.11
        assert totals['p95_ms'] == _expected_p95_ms

        # .. the overview's related entities are the callers, including the anonymous one ..
        assert totals['related_count'] == 3

        # .. channels rank by traffic ..
        top_channels = overview['top_channels']
        assert len(top_channels) == 2
        assert top_channels[0]['name'] == _channel_a
        assert top_channels[0]['request_count'] == 135
        assert top_channels[0]['error_count'] == 15
        assert top_channels[0]['related_count'] == 3
        assert top_channels[1]['name'] == _channel_b
        assert top_channels[1]['request_count'] == 50

        # .. consumers rank by traffic and the anonymous bucket has its display name ..
        top_consumers = overview['top_consumers']
        assert len(top_consumers) == 3
        assert top_consumers[0]['name'] == _caller_alice
        assert top_consumers[0]['request_count'] == 110
        assert top_consumers[1]['name'] == _caller_bob
        assert top_consumers[1]['request_count'] == 70
        assert top_consumers[2]['name'] == Caller_Anonymous
        assert top_consumers[2]['request_count'] == 5

        # .. each ranked row carries a sparkline ..
        assert top_channels[0]['spark'] == [110, 25]

        # .. and the timeline splits each period into its ok and error series.
        timeline = overview['timeline']

        expected_timeline = [
            {'ts_ms': period_to_ms(_period_ten), 'series': 'ok', 'count': 100, 'is_anomaly': False},
            {'ts_ms': period_to_ms(_period_ten), 'series': 'error', 'count': 10, 'is_anomaly': False},
            {'ts_ms': period_to_ms(_period_eleven), 'series': 'ok', 'count': 70, 'is_anomaly': False},
            {'ts_ms': period_to_ms(_period_eleven), 'series': 'error', 'count': 5, 'is_anomaly': False},
        ]

        assert timeline == expected_timeline

        # The per-channel screen scopes everything down to one channel ..
        channel_data = get_channel(_now, Range_Day, _channel_a)

        assert channel_data['name'] == _channel_a
        assert channel_data['source'] == AuditSource.REST_Channel
        assert channel_data['totals']['request_count'] == 135

        # .. its consumer breakdown ranks this channel's callers only ..
        channel_rows = channel_data['rows']
        assert len(channel_rows) == 3
        assert channel_rows[0]['name'] == _caller_alice
        assert channel_rows[0]['request_count'] == 110
        assert channel_rows[1]['name'] == _caller_bob
        assert channel_rows[1]['request_count'] == 20
        assert channel_rows[2]['name'] == Caller_Anonymous
        assert channel_rows[2]['request_count'] == 5

        # .. and the error-source split is the why behind the error count.
        error_sources = channel_data['error_sources']
        assert error_sources == {'auth': 10, 'rate_limit': 5, 'upstream': 0, 'gateway': 0}

        # The per-consumer screen shows everything one credential does across all channels ..
        consumer_data = get_consumer(_now, Range_Day, _caller_bob)

        assert consumer_data['name'] == _caller_bob
        assert consumer_data['totals']['request_count'] == 70
        assert consumer_data['totals']['last_seen'] == _period_eleven

        consumer_rows = consumer_data['rows']
        assert len(consumer_rows) == 2
        assert consumer_rows[0]['name'] == _channel_b
        assert consumer_rows[0]['request_count'] == 50
        assert consumer_rows[1]['name'] == _channel_a
        assert consumer_rows[1]['request_count'] == 20

        # .. and the anonymous page holds only the requests that never authenticated.
        anonymous_data = get_consumer(_now, Range_Day, Caller_Anonymous)

        assert anonymous_data['totals']['request_count'] == 5

        anonymous_rows = anonymous_data['rows']
        assert len(anonymous_rows) == 1
        assert anonymous_rows[0]['name'] == _channel_a
        assert anonymous_rows[0]['request_count'] == 5

        # Each CSV renders the same rows its screen shows, headers first.
        overview_content = overview_csv(overview)
        overview_lines = overview_content.splitlines()
        assert overview_lines[0] == 'channel,requests,errors,error_rate,p95_ms,consumers'
        assert overview_lines[1] == f'{_channel_a},135,15,11.11,{_expected_p95_ms},3'
        assert overview_lines[2] == f'{_channel_b},50,0,0.0,{_expected_p95_ms},1'

        channel_content = channel_csv(channel_data)
        channel_lines = channel_content.splitlines()
        assert channel_lines[0] == 'consumer,requests,errors,error_rate,p95_ms,last_seen'
        assert channel_lines[1] == f'{_caller_alice},110,10,9.09,{_expected_p95_ms},{_period_ten}'

        consumer_content = consumer_csv(consumer_data)
        consumer_lines = consumer_content.splitlines()
        assert consumer_lines[0] == 'channel,requests,errors,error_rate,p95_ms,last_seen'
        assert consumer_lines[1] == f'{_channel_b},50,0,0.0,{_expected_p95_ms},{_period_eleven}'

# ################################################################################################################################

def test_analytics_views_empty_store(tmp_path:'os.PathLike') -> 'None':
    """ A fresh install has an empty store - every screen still answers, with zeros
    and empty tables, never with an error.
    """
    db_path = os.path.join(str(tmp_path), 'analytics-empty.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env('Zato_Analytics_DB_', details):

        overview = get_overview(_now, Range_Day)

        assert overview['totals']['request_count'] == 0
        assert overview['totals']['error_rate'] == 0.0
        assert overview['totals']['p95_ms'] == 0
        assert overview['top_channels'] == []
        assert overview['top_consumers'] == []
        assert overview['timeline'] == []

        channel_data = get_channel(_now, Range_Day, 'no.such.channel')

        assert channel_data['totals']['request_count'] == 0
        assert channel_data['rows'] == []
        assert channel_data['source'] == ''
        assert channel_data['error_sources'] == {'auth': 0, 'rate_limit': 0, 'upstream': 0, 'gateway': 0}

        consumer_data = get_consumer(_now, Range_Day, 'no.such.caller')

        assert consumer_data['totals']['request_count'] == 0
        assert consumer_data['rows'] == []

        # The CSVs of an empty store are their headers and nothing else
        overview_content = overview_csv(overview)
        channel_content = channel_csv(channel_data)
        consumer_content = consumer_csv(consumer_data)

        assert overview_content.splitlines() == ['channel,requests,errors,error_rate,p95_ms,consumers']
        assert channel_content.splitlines() == ['consumer,requests,errors,error_rate,p95_ms,last_seen']
        assert consumer_content.splitlines() == ['channel,requests,errors,error_rate,p95_ms,last_seen']

# ################################################################################################################################
# ################################################################################################################################
