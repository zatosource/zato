# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from _client import ZatoClient

SERVICE = 'zato.pubsub.permission'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

def _get_sec_id(client):
    """Get the first available security definition ID."""
    data, _ = client.get_list('zato.security.basic-auth.get-list', cluster_id=1)
    if data:
        return data[0]['id']
    raise Exception('No security definitions found')

class TestPubSubPermission:
    created_ids = []
    sec_id = None

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        self.__class__.sec_id = _get_sec_id(client)
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            sec_base_id=self.__class__.sec_id,
            pub='topic-a,topic-b',
            sub='topic-c',
        )
        assert 'id' in resp
        assert resp['security'] == 'admin.invoke'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        sec_ids = [item.get('sec_base_id', '') for item in data]
        assert self.__class__.sec_id in sec_ids

    def test_04_create_batch(self, client):
        for i in range(2, 6):
            sec_name = f'test-perm-sec-{i}'
            sec_resp = client.create('zato.security.basic-auth.create',
                cluster_id=1,
                name=sec_name,
                is_active=True,
                username=f'permuser{i}',
                realm='testrealm',
            )
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                sec_base_id=sec_resp['id'],
                pub=f'topic-pub-{i}',
                sub=f'topic-sub-{i}',
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item.get('security', '').startswith('test-perm-sec-')]
        assert len(test_items) >= 4

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            sec_base_id=self.__class__.sec_id,
            pub='topic-a-edited',
            sub='topic-c-edited',
        )
        assert resp['id']

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        for item in data:
            if item.get('sec_base_id') == self.__class__.sec_id:
                assert 'topic-a-edited' in item.get('pub', [])
                return
        raise AssertionError(f'Permission for sec_base_id={self.__class__.sec_id} not found after edit')

    def test_08_ping(self, client):
        pytest.skip('No ping service for pub/sub permissions')

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item.get('security', '').startswith('test-perm-sec-')]
        assert len(test_items) >= 3

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item.get('security', '').startswith('test-perm-sec-')]
        assert len(test_items) == 0
