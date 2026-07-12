# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from datetime import datetime, timezone

# PyPI
import pytest

# Zato - test utilities
from zato.common.test.client import AdminClient as ZatoClient

SERVICE = 'zato.scheduler.job'

@pytest.fixture(scope='module')
def client(zato_server):
    out = ZatoClient(zato_server['base_url'], zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGetCurrentStateResponse:
    """ Verifies that get-current-state returns chart_buckets and recent_events
    instead of the old history_timeline.
    """

    created_ids = []

    def _start_date(self) -> 'str':
        return datetime.now(timezone.utc).isoformat()

    # ##############################################################################################################################

    def test_01_create_job(self, client) -> 'None':
        response = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-incremental-poll-job',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            hours=24,
        )
        assert 'id' in response
        self.__class__.created_ids.append(response['id'])

    # ##############################################################################################################################

    def test_02_execute_job(self, client) -> 'None':
        item_id = self.__class__.created_ids[0]
        client.invoke(f'{SERVICE}.execute', {'job_id': item_id})
        time.sleep(2)

    # ##############################################################################################################################

    def test_03_get_current_state_has_chart_buckets(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {})
        assert 'chart_buckets' in response
        chart_buckets = response['chart_buckets']
        assert 'buckets' in chart_buckets
        assert len(chart_buckets['buckets']) == 120

    # ##############################################################################################################################

    def test_04_get_current_state_has_recent_events(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {})
        assert 'recent_events' in response
        recent_events = response['recent_events']
        assert isinstance(recent_events, list)
        assert len(recent_events) >= 1

    # ##############################################################################################################################

    def test_05_get_current_state_no_history_timeline(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {})
        assert 'history_timeline' not in response

    # ##############################################################################################################################

    def test_06_chart_buckets_have_outcome_counts(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {})
        bucket = response['chart_buckets']['buckets'][0]
        assert 'ok' in bucket
        assert 'error' in bucket
        assert 'timeout' in bucket
        assert 'skipped_already_in_flight' in bucket
        assert 'start_iso' in bucket
        assert 'end_iso' in bucket

    # ##############################################################################################################################

    def test_07_recent_events_have_expected_fields(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {})
        recent_events = response['recent_events']
        assert len(recent_events) >= 1
        event = recent_events[0]
        assert 'outcome' in event
        assert 'actual_fire_time_iso' in event
        assert 'job_id' in event
        assert 'job_name' in event

    # ##############################################################################################################################

    def test_08_chart_since_iso_filters(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {
            'chart_since_iso': '2099-01-01T00:00:00+00:00',
            'chart_until_iso': '2099-01-01T02:00:00+00:00',
        })
        chart_buckets = response['chart_buckets']
        total = 0
        for bucket in chart_buckets['buckets']:
            total += bucket['ok'] + bucket['error'] + bucket['timeout']
        assert total == 0

    # ##############################################################################################################################

    def test_09_recent_since_iso_filters(self, client) -> 'None':
        response = client.invoke(f'{SERVICE}.get-current-state', {
            'recent_since_iso': '2099-01-01T00:00:00+00:00',
        })
        recent_events = response['recent_events']
        assert len(recent_events) == 0

    # ##############################################################################################################################

    def test_99_cleanup(self, client) -> 'None':
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

# ################################################################################################################################
# ################################################################################################################################
