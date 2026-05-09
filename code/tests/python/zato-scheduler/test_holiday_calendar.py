# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyPI
import pytest

# Zato - test utilities
from _client import ZatoClient

SERVICE = 'zato.scheduler.holiday-calendar'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

# ################################################################################################################################
# ################################################################################################################################

class TestHolidayCalendarCRUD:
    """Full CRUD lifecycle for holiday calendars via the admin REST API."""

    created_ids = []

    # ##############################################################################################################################

    def test_01_get_list_initial(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        assert isinstance(data, list)

    # ##############################################################################################################################

    def test_02_create_one(self, client):
        resp = client.create(f'{SERVICE}.create',
            name='test-cal-holidays-1',
            description='Test calendar for US holidays',
            dates=['2026-12-25', '2026-01-01', '2026-07-04'],
            weekdays=[],
        )
        assert 'id' in resp
        assert resp['name'] == 'test-cal-holidays-1'
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        names = [item['name'] for item in data]
        assert 'test-cal-holidays-1' in names

    # ##############################################################################################################################

    def test_04_get_by_id(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.invoke(f'{SERVICE}.get-by-id', {'id': item_id})
        assert resp['name'] == 'test-cal-holidays-1'

    # ##############################################################################################################################

    def test_05_create_weekend_calendar(self, client):
        resp = client.create(f'{SERVICE}.create',
            name='test-cal-weekends',
            description='Skip weekends',
            dates=[],
            weekdays=[5, 6],
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_06_create_batch(self, client):
        for i in range(3, 6):
            resp = client.create(f'{SERVICE}.create',
                name=f'test-cal-batch-{i}',
                dates=[f'2026-0{i}-01'],
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_07_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        test_items = [item for item in data if item['name'].startswith('test-cal-')]
        assert len(test_items) >= 5

    # ##############################################################################################################################

    def test_08_edit_rename(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            name='test-cal-holidays-renamed',
            description='Renamed holiday calendar',
            dates=['2026-12-25', '2026-01-01'],
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_09_verify_rename(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        names = [item['name'] for item in data]
        assert 'test-cal-holidays-renamed' in names
        assert 'test-cal-holidays-1' not in names

    # ##############################################################################################################################

    def test_10_edit_add_weekdays(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            name='test-cal-holidays-renamed',
            description='Holidays plus weekends',
            dates=['2026-12-25', '2026-01-01'],
            weekdays=[5, 6],
        )
        assert resp['id'] == item_id

    # ##############################################################################################################################

    def test_11_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    # ##############################################################################################################################

    def test_12_verify_deleted(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        names = [item['name'] for item in data]
        assert 'test-cal-holidays-renamed' not in names

    # ##############################################################################################################################

    def test_13_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    # ##############################################################################################################################

    def test_14_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        test_items = [item for item in data if item['name'].startswith('test-cal-')]
        assert len(test_items) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCalendarJobIntegration:
    """Tests that a scheduler job can reference a holiday calendar."""

    created_cal_ids = []
    created_job_ids = []

    # ##############################################################################################################################

    def test_01_create_calendar(self, client):
        resp = client.create(f'{SERVICE}.create',
            name='test-integ-cal',
            dates=['2026-12-25'],
            weekdays=[5, 6],
        )
        assert 'id' in resp
        self.__class__.created_cal_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_02_create_job_with_calendar(self, client):
        from datetime import datetime, timezone as tz
        resp = client.create('zato.scheduler.job.create',
            cluster_id=1,
            name='test-integ-cal-job',
            is_active=True,
            job_type='interval_based',
            service='demo.ping',
            start_date=datetime.now(tz.utc).isoformat(),
            minutes=5,
            calendar='test-integ-cal',
        )
        assert 'id' in resp
        self.__class__.created_job_ids.append(resp['id'])

    # ##############################################################################################################################

    def test_03_verify_calendar_on_job(self, client):
        item_id = self.__class__.created_job_ids[0]
        resp = client.invoke('zato.scheduler.job.get-by-id', {'cluster_id': 1, 'id': item_id})
        assert resp.get('calendar') == 'test-integ-cal'

    # ##############################################################################################################################

    def test_99_cleanup(self, client):
        for jid in self.__class__.created_job_ids[:]:
            client.delete('zato.scheduler.job.delete', id=jid)
            self.__class__.created_job_ids.remove(jid)
        for cid in self.__class__.created_cal_ids[:]:
            client.delete(f'{SERVICE}.delete', id=cid)
            self.__class__.created_cal_ids.remove(cid)

# ################################################################################################################################
# ################################################################################################################################
