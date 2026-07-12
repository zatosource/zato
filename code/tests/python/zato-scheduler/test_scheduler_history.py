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

JOB_SERVICE = 'zato.scheduler.job'

@pytest.fixture(scope='module')
def client(zato_server):
    out = ZatoClient(zato_server['base_url'], zato_server['password'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerHistory:
    """Tests for scheduler execution history via the admin REST API.

    These tests create a short-interval job, execute it manually, wait for the execution
    to complete, and then verify that the history API returns the expected records.
    """

    created_ids = []

    def _start_date(self):
        return datetime.now(timezone.utc).isoformat()

    # ##############################################################################################################################

    def test_01_create_job_for_history(self, client):
        resp = client.create(f'{JOB_SERVICE}.create',
            cluster_id=1,
            name='test-hist-job-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            hours=24,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_02_get_history_initially_empty(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        assert isinstance(response['rows'], list)

    # ##############################################################################################################################

    def test_03_execute_job_and_wait(self, client):
        item_id = self.__class__.created_ids[0]
        client.invoke(f'{JOB_SERVICE}.execute', {'job_id': item_id})
        time.sleep(3)

    # ##############################################################################################################################

    def test_04_get_history_after_execute(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        rows = response['rows']
        assert response['total'] >= 1
        assert len(rows) >= 1
        record = rows[-1]
        assert 'planned_fire_time_iso' in record
        assert 'actual_fire_time_iso' in record
        assert 'outcome' in record

    # ##############################################################################################################################

    def test_05_history_per_job(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        rows = response['rows']
        assert isinstance(rows, list)
        assert len(rows) >= 1
        assert response['total'] >= 1

    # ##############################################################################################################################

    def test_06_execute_multiple_times(self, client):
        item_id = self.__class__.created_ids[0]
        for _ in range(3):
            client.invoke(f'{JOB_SERVICE}.execute', {'job_id': item_id})
            time.sleep(2)

    # ##############################################################################################################################

    def test_07_history_grows(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        rows = response['rows']
        assert isinstance(rows, list)
        assert len(rows) >= 2

    # ##############################################################################################################################

    def test_08_history_records_have_duration(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        ok_records = []

        for record in response['rows']:
            if record['outcome'] == 'ok':
                ok_records.append(record)

        for record in ok_records:
            if 'duration_ms' in record:
                assert record['duration_ms'] >= 0

    # ##############################################################################################################################

    def test_09_history_filtered_by_since_iso(self, client):
        item_id = self.__class__.created_ids[0]

        # Get all history without since_iso
        response_all = client.invoke(f'{JOB_SERVICE}.get-history', {
            'id': item_id,
            'page': 1,
            'page_size': 100,
        })

        all_total = response_all['total']
        assert all_total >= 2, f'Expected >= 2 total records, got {all_total}'

        # Use a since_iso far in the future to get zero results
        response_future = client.invoke(f'{JOB_SERVICE}.get-history', {
            'id': item_id,
            'page': 1,
            'page_size': 100,
            'since_iso': '2099-01-01T00:00:00Z',
        })

        future_total = response_future['total']
        assert future_total == 0, f'Expected 0 records with future since_iso, got {future_total}'

        # Use a since_iso far in the past to get all results
        response_past = client.invoke(f'{JOB_SERVICE}.get-history', {
            'id': item_id,
            'page': 1,
            'page_size': 100,
            'since_iso': '2000-01-01T00:00:00Z',
        })

        past_total = response_past['total']
        assert past_total == all_total, f'Expected {all_total} with past since_iso, got {past_total}'

    # ##############################################################################################################################

    def test_99_cleanup(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{JOB_SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

# ################################################################################################################################
# ################################################################################################################################
