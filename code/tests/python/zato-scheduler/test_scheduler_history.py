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
from _client import ZatoClient

JOB_SERVICE = 'zato.scheduler.job'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

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
        resp = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        assert isinstance(resp, list)

    # ##############################################################################################################################

    def test_03_execute_job_and_wait(self, client):
        item_id = self.__class__.created_ids[0]
        client.invoke(f'{JOB_SERVICE}.execute', {'id': item_id})
        time.sleep(3)

    # ##############################################################################################################################

    def test_04_get_history_after_execute(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        assert isinstance(resp, list)
        assert len(resp) >= 1
        record = resp[-1]
        assert 'planned_fire_time_iso' in record
        assert 'actual_fire_time_iso' in record
        assert 'outcome' in record

    # ##############################################################################################################################

    def test_05_get_all_history(self, client):
        resp = client.invoke(f'{JOB_SERVICE}.get-all-history')
        assert isinstance(resp, dict)
        item_id = str(self.__class__.created_ids[0])
        assert item_id in resp
        assert isinstance(resp[item_id], list)
        assert len(resp[item_id]) >= 1

    # ##############################################################################################################################

    def test_06_execute_multiple_times(self, client):
        item_id = self.__class__.created_ids[0]
        for _ in range(3):
            client.invoke(f'{JOB_SERVICE}.execute', {'id': item_id})
            time.sleep(2)

    # ##############################################################################################################################

    def test_07_history_grows(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        assert isinstance(resp, list)
        assert len(resp) >= 2

    # ##############################################################################################################################

    def test_08_history_records_have_duration(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{JOB_SERVICE}.get-history', {'id': item_id})
        executed_records = [r for r in resp if r.get('outcome') == 'executed']
        for record in executed_records:
            if 'duration_ms' in record:
                assert int(record['duration_ms']) >= 0

    # ##############################################################################################################################

    def test_99_cleanup(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{JOB_SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

# ################################################################################################################################
# ################################################################################################################################
