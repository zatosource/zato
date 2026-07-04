# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient

if 0:
    from zato.common.typing_ import any_

SERVICE = 'zato.pubsub.permission'

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'ZatoClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

def _get_sec_info(client:'ZatoClient') -> 'tuple':
    """Get the first available security definition ID and name."""
    data, _ = client.get_list('zato.security.basic-auth.get-list', cluster_id=1)
    if data:
        return data[0]['id'], data[0]['name']
    raise Exception('No security definitions found')

class TestPubSubPermission:
    created_ids = []
    sec_id = None
    sec_name = None

    def test_01_get_list_empty(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_02_create_one(self, client:'ZatoClient') -> 'None':
        self.__class__.sec_id, self.__class__.sec_name = _get_sec_info(client)
        response = client.create(f'{SERVICE}.create',
            cluster_id=1,
            sec_base_id=self.__class__.sec_id,
            pattern='pub=topic-a\npub=topic-b\nsub=topic-c',
            access_type='publisher-subscriber',
        )
        assert 'id' in response
        assert response['security'] == self.__class__.sec_name
        self.__class__.created_ids.append(response['id'])

    def test_03_get_list_after_create(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        sec_ids = [item['sec_base_id'] for item in data]
        assert self.__class__.sec_id in sec_ids

    def test_04_create_batch(self, client:'ZatoClient') -> 'None':
        for i in range(2, 6):
            sec_name = f'test-perm-sec-{i}'
            sec_response = client.create('zato.security.basic-auth.create',
                cluster_id=1,
                name=sec_name,
                is_active=True,
                username=f'permuser{i}',
                realm='testrealm',
            )
            response = client.create(f'{SERVICE}.create',
                cluster_id=1,
                sec_base_id=sec_response['id'],
                pattern=f'pub=topic-pub-{i}\nsub=topic-sub-{i}',
                access_type='publisher-subscriber',
            )
            assert 'id' in response
            self.__class__.created_ids.append(response['id'])

    def test_05_get_list_batch(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-perm-sec-')]
        assert len(test_items) >= 4

    def test_06_edit_one(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids[0]
        response = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            sec_base_id=self.__class__.sec_id,
            pattern='pub=topic-a-edited\nsub=topic-c-edited',
            access_type='publisher-subscriber',
        )
        assert response['id']

    def test_07_get_list_after_edit(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        # More than one permission may exist for this security definition
        # so look for the edited pattern among all of them.
        patterns = [item['pattern'] for item in data if item['sec_base_id'] == self.__class__.sec_id]
        assert patterns, f'No permissions for sec_base_id={self.__class__.sec_id} found after edit'
        assert any('topic-a-edited' in pattern for pattern in patterns)

    def test_08_ping(self, client:'ZatoClient') -> 'None':
        pytest.skip('No ping service for pub/sub permissions')

    def test_09_delete_one(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids.pop(0)
        _ = client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-perm-sec-')]
        assert len(test_items) >= 3

    def test_11_delete_rest(self, client:'ZatoClient') -> 'None':
        for item_id in self.__class__.created_ids[:]:
            _ = client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-perm-sec-')]
        assert len(test_items) == 0
