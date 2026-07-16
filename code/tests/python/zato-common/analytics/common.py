# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_sql.asserts import assert_mysql_connection_encrypted as assert_mysql_engine_encrypted, \
    assert_postgresql_connection_encrypted as assert_postgresql_engine_encrypted
from live_sql.env import database_env
from zato.common.analytics.api import get_analytics_engine, get_latency_bucket_index, usage_table, watermark_table, \
    Latency_Bucket_Count, Latency_Buckets_Ms
from zato.common.analytics.query import get_percentile
from zato.common.analytics.rollup import run_rollup
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import anydict, anylist, intlist, stranydict

    envgen = Iterator[None]
    anylist = anylist
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The prefixes both stores' environment variables share
_audit_env_prefix     = 'Zato_Audit_Log_DB_'
_analytics_env_prefix = 'Zato_Analytics_DB_'

# The server name all the test events are written under
_server_name = 'test-analytics-server'

# The channels the test events belong to
_channel_a = 'analytics.test.channel.a'
_channel_b = 'analytics.test.channel.b'

# The credentials the test events were authenticated with - the empty
# one is a request that failed authentication.
_caller_alice = 'analytics.test.alice'
_caller_bob   = 'analytics.test.bob'
_caller_carol = 'analytics.test.carol'

# The hourly periods the controlled events land in
_period_one = '2026-07-14T10'
_period_two = '2026-07-14T11'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def analytics_test_env(details:'stranydict') -> 'envgen':
    """ Points both the audit log and the analytics store at one backend for the duration
    of a test - the two schemas share the database without any table name clashes.
    """
    with database_env(_audit_env_prefix, details):
        with database_env(_analytics_env_prefix, details):
            yield

# ################################################################################################################################

def _insert_event(
    *,
    source:'str',
    event_type:'str',
    channel:'str',
    caller:'str',
    event_time_iso:'str',
    status:'str',
    duration_ms:'int',
    size:'int',
) -> 'None':
    """ Writes one audit event with a controlled event time, which is how the test
    places events in known hourly periods.
    """
    event_time_iso = f'{event_time_iso}:00:00+00:00'

    insert_statement = event_table.insert().values(
        cid='cid-analytics-test',
        source=source,
        event_type=event_type,
        object_name=channel,
        msg_id='',
        correl_id='',
        ext_client_id=caller,
        pub_time_iso='',
        event_time_iso=event_time_iso,
        server_name=_server_name,
        endpoint='analytics.test.service',
        sub_key='',
        size=size,
        priority=0,
        outcome=AuditOutcome.OK,
        status=status,
        duration_ms=duration_ms,
        data='',
    )

    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(insert_statement)

# ################################################################################################################################

def _clean_tables() -> 'None':
    """ Starts from empty tables because containers and SQLite files can be reused between runs.
    """
    audit_engine = get_audit_engine()

    with audit_engine.begin() as connection:
        _ = connection.execute(event_table.delete())

    analytics_engine = get_analytics_engine()

    with analytics_engine.begin() as connection:
        _ = connection.execute(usage_table.delete())
        _ = connection.execute(watermark_table.delete())

# ################################################################################################################################

def _load_usage_rows() -> 'anydict':
    """ Reads all the hourly rows, keyed by (period, channel, caller, status class).
    """
    statement = select(
        usage_table.c.period,
        usage_table.c.source,
        usage_table.c.channel,
        usage_table.c.caller,
        usage_table.c.status_class,
        usage_table.c.request_count,
        usage_table.c.error_count_auth,
        usage_table.c.error_count_rate_limit,
        usage_table.c.error_count_upstream,
        usage_table.c.error_count_gateway,
        usage_table.c.size_sum,
        usage_table.c.duration_sum_ms,
        usage_table.c.latency_buckets,
    )

    engine = get_analytics_engine()

    # Our response to produce
    out:'anydict' = {}

    with engine.connect() as connection:
        result = connection.execute(statement)

        for period, source, channel, caller, status_class, request_count, count_auth, count_rate_limit, \
            count_upstream, count_gateway, size_sum, duration_sum_ms, latency_buckets_json in result:

            key = (period, channel, caller, status_class)

            out[key] = {
                'source': source,
                'request_count': request_count,
                'error_count_auth': count_auth,
                'error_count_rate_limit': count_rate_limit,
                'error_count_upstream': count_upstream,
                'error_count_gateway': count_gateway,
                'size_sum': size_sum,
                'duration_sum_ms': duration_sum_ms,
                'latency_buckets': loads(latency_buckets_json),
            }

    return out

# ################################################################################################################################

def _get_watermark() -> 'int':
    """ Reads the current watermark of the analytics store.
    """
    statement = select(watermark_table.c.last_event_id)

    engine = get_analytics_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.fetchone()

    out = row[0]
    return out

# ################################################################################################################################

def _get_max_event_id() -> 'int':
    """ Reads the id of the newest channel response in the audit log.
    """
    statement = select(event_table.c.id)
    statement = statement.where(event_table.c.event_type == AuditEvent.Response_Sent)
    statement = statement.where(event_table.c.source == AuditSource.REST_Channel)
    statement = statement.order_by(event_table.c.id.desc())
    statement = statement.limit(1)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.fetchone()

    out = row[0]
    return out

# ################################################################################################################################

def _expected_buckets(*durations_ms:'int') -> 'intlist':
    """ Builds the latency histogram the given durations should produce.
    """

    # Our response to produce
    out:'intlist' = [0] * Latency_Bucket_Count

    for duration_ms in durations_ms:
        index = get_latency_bucket_index(duration_ms)
        out[index] += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_rollup_scenario() -> 'None':
    """ The complete rollup scenario every backend must pass: aggregation correctness
    against known rows, watermark advance, idempotent re-runs, incremental upserts,
    percentile computation out of bucket counts, and credential and duration
    presence on events written through the real audit log writer.
    """
    _clean_tables()

    # Events the rollup must ignore go in first, so the watermark assertion below
    # can compare against the id of the newest channel response ..
    _insert_event(source=AuditSource.PubSub, event_type=AuditEvent.Published, channel='analytics.test.topic',
        caller='', event_time_iso=_period_one, status='', duration_ms=0, size=1)

    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Request_Received, channel=_channel_a,
        caller='', event_time_iso=_period_one, status='', duration_ms=0, size=1)

    # .. three successes of one caller in one hour, with known durations and sizes ..
    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller=_caller_alice, event_time_iso=_period_one, status='200 OK', duration_ms=10, size=100)

    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller=_caller_alice, event_time_iso=_period_one, status='200 OK', duration_ms=30, size=200)

    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller=_caller_alice, event_time_iso=_period_one, status='200 OK', duration_ms=3000, size=300)

    # .. an authorization failure of the same caller ..
    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller=_caller_alice, event_time_iso=_period_one, status='403 Forbidden', duration_ms=5, size=50)

    # .. a rate-limited request that never authenticated, so it has no caller ..
    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller='', event_time_iso=_period_one, status='429 Too Many Requests', duration_ms=1, size=10)

    # .. and another channel's caller in the next hour.
    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_b,
        caller=_caller_bob, event_time_iso=_period_two, status='200 OK', duration_ms=100, size=20)

    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_b,
        caller=_caller_bob, event_time_iso=_period_two, status='200 OK', duration_ms=100, size=30)

    # The first run aggregates the seven channel responses and nothing else ..
    result = run_rollup()
    assert result.event_count == 7, f'Expected 7 events aggregated, got {result.event_count}'

    # .. and the watermark now points at the newest channel response.
    max_event_id = _get_max_event_id()
    watermark = _get_watermark()
    assert result.last_event_id == max_event_id
    assert watermark == max_event_id

    rows = _load_usage_rows()
    assert len(rows) == 4, f'Expected 4 hourly rows, got {len(rows)}: {sorted(rows)}'

    # The three successes fold into one 2xx row with summed sizes and durations
    # and one histogram count per duration ..
    alice_ok = rows[(_period_one, _channel_a, _caller_alice, '2xx')]
    assert alice_ok['source'] == AuditSource.REST_Channel
    assert alice_ok['request_count'] == 3
    assert alice_ok['size_sum'] == 600
    assert alice_ok['duration_sum_ms'] == 3040
    assert alice_ok['error_count_auth'] == 0
    assert alice_ok['latency_buckets'] == _expected_buckets(10, 30, 3000)

    # .. the authorization failure is an auth error in its own 4xx row ..
    alice_error = rows[(_period_one, _channel_a, _caller_alice, '4xx')]
    assert alice_error['request_count'] == 1
    assert alice_error['error_count_auth'] == 1
    assert alice_error['error_count_rate_limit'] == 0

    # .. the rate-limited request lands under the anonymous caller ..
    anonymous = rows[(_period_one, _channel_a, '', '4xx')]
    assert anonymous['request_count'] == 1
    assert anonymous['error_count_rate_limit'] == 1
    assert anonymous['error_count_auth'] == 0

    # .. and the other channel's hour holds both of its successes.
    bob_ok = rows[(_period_two, _channel_b, _caller_bob, '2xx')]
    assert bob_ok['request_count'] == 2
    assert bob_ok['size_sum'] == 50
    assert bob_ok['duration_sum_ms'] == 200
    assert bob_ok['latency_buckets'] == _expected_buckets(100, 100)

    # Rerunning from the same watermark changes nothing - there is nothing new to read ..
    rerun_result = run_rollup()
    assert rerun_result.event_count == 0
    assert rerun_result.last_event_id == max_event_id

    rows_after_rerun = _load_usage_rows()
    assert rows_after_rerun == rows, 'Expected an idempotent re-run to leave the rows unchanged'

    # .. while a new event folds into the already existing hourly row.
    _insert_event(source=AuditSource.REST_Channel, event_type=AuditEvent.Response_Sent, channel=_channel_a,
        caller=_caller_alice, event_time_iso=_period_one, status='200 OK', duration_ms=10, size=100)

    incremental_result = run_rollup()
    assert incremental_result.event_count == 1
    assert incremental_result.last_event_id > max_event_id

    rows = _load_usage_rows()
    alice_ok = rows[(_period_one, _channel_a, _caller_alice, '2xx')]
    assert alice_ok['request_count'] == 4
    assert alice_ok['size_sum'] == 700
    assert alice_ok['duration_sum_ms'] == 3050
    assert alice_ok['latency_buckets'] == _expected_buckets(10, 30, 3000, 10)

    # Percentiles come out of bucket counts by linear interpolation inside the target bucket ..
    buckets = [0] * Latency_Bucket_Count
    buckets[0] = 100

    # .. all requests are in the first bucket, whose boundaries are 0 and 5 ms ..
    assert get_percentile(buckets, 0.95) == 4

    # .. everything in the overflow bucket answers with the last known boundary ..
    overflow_buckets = [0] * Latency_Bucket_Count
    overflow_buckets[-1] = 1
    assert get_percentile(overflow_buckets, 0.95) == Latency_Buckets_Ms[-1]

    # .. and an empty histogram has no percentiles.
    empty_buckets = [0] * Latency_Bucket_Count
    assert get_percentile(empty_buckets, 0.95) == 0

    # Events written through the real audit log writer carry the credential and the duration
    # from 3.1-3.2, and the rollup picks both up.
    audit_log = AuditLog(_server_name)
    audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _channel_a,
        ext_client_id=_caller_carol, status='200 OK', duration_ms=42, size=7)

    writer_result = run_rollup()
    assert writer_result.event_count == 1

    rows = _load_usage_rows()

    # The writer stamps the current time, so the row's period is found by its caller
    carol_rows:'anylist' = []

    for key in rows:
        _, _, caller, _ = key
        if caller == _caller_carol:
            carol_rows.append(rows[key])

    assert len(carol_rows) == 1, f'Expected one row for {_caller_carol}, got {len(carol_rows)}'

    carol = carol_rows[0]
    assert carol['request_count'] == 1
    assert carol['duration_sum_ms'] == 42
    assert carol['size_sum'] == 7
    assert carol['latency_buckets'] == _expected_buckets(42)

# ################################################################################################################################

def assert_mysql_connection_encrypted() -> 'None':
    """ Confirms the current MySQL session of the analytics store really is encrypted.
    """
    engine = get_analytics_engine()
    assert_mysql_engine_encrypted(engine)

# ################################################################################################################################

def assert_postgresql_connection_encrypted() -> 'None':
    """ Confirms the current PostgreSQL session of the analytics store really is encrypted.
    """
    engine = get_analytics_engine()
    assert_postgresql_engine_encrypted(engine)

# ################################################################################################################################
# ################################################################################################################################
