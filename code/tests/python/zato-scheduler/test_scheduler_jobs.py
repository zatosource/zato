# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# PyPI
import pytest

# Zato - test utilities
from _client import ZatoClient

SERVICE = 'zato.scheduler.job'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerJobsCRUD:
    """Full CRUD lifecycle for scheduler jobs via the admin REST API."""

    created_ids = []

    def _start_date(self):
        return datetime.now(timezone.utc).isoformat()

    # ##############################################################################################################################

    def test_01_get_list_initial(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    # ##############################################################################################################################

    def test_02_create_interval_job(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-sched-job-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=10,
        )
        assert 'id' in resp
        assert resp['name'] == 'test-sched-job-1'
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        names = [item['name'] for item in data]
        assert 'test-sched-job-1' in names

    # ##############################################################################################################################

    def test_04_create_one_time_job(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-sched-onetime-1',
            is_active=True,
            job_type='one_time',
            service='demo.ping',
            start_date='2099-12-31T23:59:59',
        )
        assert 'id' in resp
        assert resp['name'] == 'test-sched-onetime-1'
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_05_create_batch_interval_jobs(self, client):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name=f'test-sched-job-{i}',
                is_active=True,
                job_type='interval_based',
                service='demo.ping',
                start_date=self._start_date(),
                minutes=10 + i,
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_06_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-sched-')]
        assert len(test_items) >= 6

    # ##############################################################################################################################

    def test_07_get_by_id(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert resp['name'] == 'test-sched-job-1'
        assert resp['job_type'] == 'interval_based'

    # ##############################################################################################################################

    def test_08_get_by_name(self, client):
        resp = client.invoke(f'{SERVICE}.get-by-name', {'cluster_id': 1, 'name': 'test-sched-job-1'})
        assert resp['name'] == 'test-sched-job-1'

    # ##############################################################################################################################

    def test_09_edit_rename(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-sched-job-1-renamed',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=15,
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_10_verify_rename(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        names = [item['name'] for item in data]
        assert 'test-sched-job-1-renamed' in names
        assert 'test-sched-job-1' not in names

    # ##############################################################################################################################

    def test_11_edit_change_interval(self, client):
        item_id = self.__class__.created_ids[2]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-sched-job-2',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            hours=1,
            minutes=30,
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_12_edit_deactivate(self, client):
        item_id = self.__class__.created_ids[2]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-sched-job-2',
            is_active=False,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            hours=1,
            minutes=30,
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_13_verify_deactivated(self, client):
        item_id = self.__class__.created_ids[2]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert resp['is_active'] in (False, 'False', 0, '0', '')

    # ##############################################################################################################################

    def test_14_execute_job(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{SERVICE}.execute', {'id': item_id})
        assert resp is not None

    # ##############################################################################################################################

    def test_15_duplicate_name_rejected(self, client):
        with pytest.raises(Exception, match='already exists'):
            client.create(f'{SERVICE}.create',
                cluster_id=1,
                name='test-sched-job-1-renamed',
                is_active=True,
                job_type='interval_based',
                service='demo.ping',
                start_date=self._start_date(),
                minutes=5,
            )

    # ##############################################################################################################################

    def test_16_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    # ##############################################################################################################################

    def test_17_verify_deleted(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        names = [item['name'] for item in data]
        assert 'test-sched-job-1-renamed' not in names

    # ##############################################################################################################################

    def test_18_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    # ##############################################################################################################################

    def test_19_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-sched-')]
        assert len(test_items) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerJobsNewFields:
    """Tests for new scheduler fields: jitter_ms, timezone, calendar, max_execution_time_ms."""

    created_ids = []

    def _start_date(self):
        return datetime.now(timezone.utc).isoformat()

    # ##############################################################################################################################

    def test_01_create_with_jitter(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-sched-jitter-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=5,
            jitter_ms=500,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_02_verify_jitter_persisted(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert int(resp.get('jitter_ms', 0)) == 500

    # ##############################################################################################################################

    def test_03_create_with_timezone(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-sched-tz-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=10,
            timezone='America/New_York',
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_04_verify_timezone_persisted(self, client):
        item_id = self.__class__.created_ids[1]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert resp.get('timezone') == 'America/New_York'

    # ##############################################################################################################################

    def test_05_create_with_max_execution_time(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-sched-maxexec-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=10,
            max_execution_time_ms=120000,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_06_verify_max_execution_time_persisted(self, client):
        item_id = self.__class__.created_ids[2]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert int(resp.get('max_execution_time_ms', 0)) == 120000

    # ##############################################################################################################################

    def test_07_edit_add_all_new_fields(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-sched-jitter-1',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=self._start_date(),
            minutes=5,
            jitter_ms=1000,
            timezone='Europe/Prague',
            max_execution_time_ms=60000,
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_08_verify_all_new_fields(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert int(resp.get('jitter_ms', 0)) == 1000
        assert resp.get('timezone') == 'Europe/Prague'
        assert int(resp.get('max_execution_time_ms', 0)) == 60000

    # ##############################################################################################################################

    def test_09_cleanup(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

# ################################################################################################################################
# ################################################################################################################################
