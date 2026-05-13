# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from _client import ZatoClient

SERVICE = 'zato.groups'
GROUP_TYPE = 'api-clients'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

class TestSecurityGroups:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        resp = client.create(f'{SERVICE}.create',
            group_type=GROUP_TYPE,
            name='test-group-1',
        )
        assert 'id' in resp
        assert resp['name'] == 'test-group-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        names = [item['name'] for item in data]
        assert 'test-group-1' in names

    def test_04_create_batch(self, client):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                group_type=GROUP_TYPE,
                name=f'test-group-{i}',
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        test_items = [item for item in data if item['name'].startswith('test-group-')]
        assert len(test_items) >= 5

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            group_type=GROUP_TYPE,
            name='test-group-1-edited',
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        names = [item['name'] for item in data]
        assert 'test-group-1-edited' in names
        assert 'test-group-1' not in names

    def test_08_ping(self, client):
        pytest.skip('No ping service for groups')

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        test_items = [item for item in data if item['name'].startswith('test-group-')]
        assert len(test_items) >= 4

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', group_type=GROUP_TYPE)
        test_items = [item for item in data if item['name'].startswith('test-group-')]
        assert len(test_items) == 0
