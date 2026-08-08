# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The activity strip endpoint answers with the matching events cut into time buckets,
# each bucket counting its events per outcome - the same filters the poll reads,
# so the strip always shows what the listing shows.

# stdlib
import os
from contextlib import contextmanager
from json import dumps, loads

# Zato
from zato.admin.web.views.audit_log import strip
from zato.admin.web.views.audit_log.views import _strip_max_buckets, _strip_min_buckets
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource, \
    ModuleCtx as AuditLogCtx
from zato.common.ext.bunch import Bunch

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict, anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server and channel the events of these tests are written under
_server_name = 'test-activity-strip-server'
_channel_name = 'test.activity.strip.channel'

# A second channel proving that the strip honors the filters
_other_channel_name = 'test.activity.strip.other'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# Three events over exactly two hours - the window the strip derives is two hours wide,
# and with sixteen buckets each one is 7.5 minutes, so the events land in the first
# bucket, the middle one and - the window's very last moment - the last one.
_first_time_iso = '2026-01-01T10:00:00+00:00'
_middle_time_iso = '2026-01-01T11:00:00+00:00'
_last_time_iso = '2026-01-01T12:00:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

def _insert_event(connection:'any_', object_name:'str', event_time_iso:'str', outcome:'str') -> 'None':
    insert = event_table.insert().values(
        cid='cid-activity-strip',
        source=AuditSource.MLLP_Channel,
        event_type=AuditEvent.Message_Received,
        object_name=object_name,
        msg_id='',
        correl_id='',
        ext_client_id='',
        pub_time_iso='',
        event_time_iso=event_time_iso,
        server_name=_server_name,
        endpoint='',
        sub_key='',
        size=10,
        priority=0,
        outcome=outcome,
        data='MSH|^~\\&|',
    )

    _ = connection.execute(insert)

# ################################################################################################################################

@contextmanager
def _strip_events(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database holding three events of one channel
    spread over two hours, and one more event of another channel.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details_config = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details_config):

        # Creating the log creates the schema the events are inserted straight into -
        # straight, because their times have to be exact for the buckets to be known.
        _ = AuditLog(_server_name)

        engine = get_audit_engine()

        with engine.begin() as connection:
            _insert_event(connection, _channel_name, _first_time_iso, AuditOutcome.OK)
            _insert_event(connection, _channel_name, _middle_time_iso, AuditOutcome.Error)
            _insert_event(connection, _channel_name, _last_time_iso, AuditOutcome.OK)
            _insert_event(connection, _other_channel_name, _middle_time_iso, AuditOutcome.OK)

        yield

# ################################################################################################################################

def _new_request(body:'anydict') -> 'Bunch':
    out = Bunch()

    out.method = 'POST'
    out.body = dumps(body).encode('utf-8')

    return out

# ################################################################################################################################

def _get_buckets(tmp_path:'any_', **overrides:'any_') -> 'anylist':
    """ Calls the strip view with the standard filter keys, any of them overridden,
    and returns the buckets it answered with.
    """
    body = {
        'sources': [],
        'object_names': [_channel_name],
        'outcomes': [],
        'query': '',
        'status': '',
        'time_from': '',
        'time_to': '',
        'event_types': [],
        'bucket_count': _strip_min_buckets,
    }

    body.update(overrides)

    with _strip_events(tmp_path):
        response = strip(_new_request(body))

    parsed = loads(response.content)

    out = parsed['buckets']

    return out

# ################################################################################################################################

def _count(bucket:'anydict', outcome:'str') -> 'int':
    counts = bucket['counts']

    if outcome in counts:
        return counts[outcome]

    return 0

# ################################################################################################################################

def _totals(buckets:'anylist') -> 'anydict':
    out:'anydict' = {}

    for bucket in buckets:
        for outcome, count in bucket['counts'].items():

            if outcome not in out:
                out[outcome] = 0

            out[outcome] += count

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBuckets:

    def test_the_window_is_what_the_events_cover(self, tmp_path:'os.PathLike'):
        buckets = _get_buckets(tmp_path)

        assert len(buckets) == _strip_min_buckets

        assert buckets[0]['start_iso'] == _first_time_iso
        assert buckets[-1]['end_iso'] == _last_time_iso

# ################################################################################################################################

    def test_each_event_lands_in_the_bucket_its_time_says(self, tmp_path:'os.PathLike'):
        buckets = _get_buckets(tmp_path)

        # The first event opens the window, the error stands halfway through it,
        # and the window's very last moment belongs to the last bucket
        assert _count(buckets[0], AuditOutcome.OK) == 1
        assert _count(buckets[8], AuditOutcome.Error) == 1
        assert _count(buckets[-1], AuditOutcome.OK) == 1

        assert _totals(buckets) == {AuditOutcome.OK: 2, AuditOutcome.Error: 1}

# ################################################################################################################################

    def test_the_filters_narrow_what_is_counted(self, tmp_path:'os.PathLike'):
        buckets = _get_buckets(tmp_path, outcomes=[AuditOutcome.Error])

        assert _totals(buckets) == {AuditOutcome.Error: 1}

# ################################################################################################################################

    def test_nothing_matching_is_no_buckets_at_all(self, tmp_path:'os.PathLike'):
        buckets = _get_buckets(tmp_path, object_names=['no.such.channel'])

        assert buckets == []

# ################################################################################################################################

    def test_the_bucket_count_stays_within_its_bounds(self, tmp_path:'os.PathLike'):
        too_many = _get_buckets(tmp_path, bucket_count=100000)
        too_few = _get_buckets(tmp_path, bucket_count=1)

        assert len(too_many) == _strip_max_buckets
        assert len(too_few) == _strip_min_buckets

# ################################################################################################################################

    def test_one_event_still_spreads_over_the_least_window(self, tmp_path:'os.PathLike'):
        buckets = _get_buckets(tmp_path, outcomes=[AuditOutcome.Error])

        # A single event is an instant, so the window is the least one - an hour
        # ending at that event - rather than a window of no width at all
        assert buckets[0]['start_iso'] == '2026-01-01T10:00:00+00:00'
        assert buckets[-1]['end_iso'] == _middle_time_iso

        assert _count(buckets[-1], AuditOutcome.Error) == 1

# ################################################################################################################################
# ################################################################################################################################
