# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient

if 0:
    from zato.common.typing_ import any_

SERVICE = 'zato.pubsub.subscription'

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'ZatoClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

def _ensure_topic(client:'ZatoClient', name:'str') -> 'str':
    """Ensure a topic exists; return its name."""
    data, _ = client.get_list('zato.pubsub.topic.get-list', cluster_id=1)
    for item in data:
        if item['name'] == name:
            return name
    _ = client.create('zato.pubsub.topic.create', cluster_id=1, name=name, is_active=True)
    return name

def _get_or_create_sec_def(client:'ZatoClient') -> 'int':
    """Get the first available security definition ID for subscriptions."""
    data, _ = client.get_list('zato.security.basic-auth.get-list', cluster_id=1)
    if data:
        return data[0]['id']

    response = client.create('zato.security.basic-auth.create',
        name='test-pubsub-sub-sec',
        is_active=True,
        username='subtestuser',
        realm='testrealm',
    )
    return response['id']

class TestPubSubSubscription:
    created_sub_keys = []
    topic_name = None
    sec_id = None

    def test_01_get_list_empty(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_02_create_one(self, client:'ZatoClient') -> 'None':
        self.__class__.topic_name = _ensure_topic(client, '/test/sub/topic/1')
        self.__class__.sec_id = _get_or_create_sec_def(client)

        response = client.create(f'{SERVICE}.create',
            cluster_id=1,
            topic_name_list=[self.__class__.topic_name],
            sec_base_id=self.__class__.sec_id,
            delivery_type='pull',
            is_delivery_active=True,
            is_pub_active=True,
        )
        sub_key = response.get('sub_key') or response.get('id')
        assert sub_key
        self.__class__.created_sub_keys.append(sub_key)

    def test_03_get_list_after_create(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert len(data) >= 1

    def test_04_create_batch(self, client:'ZatoClient') -> 'None':
        for i in range(2, 6):
            topic = _ensure_topic(client, f'/test/sub/topic/{i}')
            response = client.create(f'{SERVICE}.create',
                cluster_id=1,
                topic_name_list=[topic],
                sec_base_id=self.__class__.sec_id,
                delivery_type='pull',
                is_delivery_active=True,
                is_pub_active=True,
            )
            sub_key = response.get('sub_key') or response.get('id')
            assert sub_key
            self.__class__.created_sub_keys.append(sub_key)

    def test_05_get_list_batch(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert len(data) >= 5

    def test_06_edit_one(self, client:'ZatoClient') -> 'None':
        sub_key = self.__class__.created_sub_keys[0]
        _ = client.edit(f'{SERVICE}.edit',
            sub_key=sub_key,
            cluster_id=1,
            topic_name_list=[self.__class__.topic_name],
            sec_base_id=self.__class__.sec_id,
            delivery_type='pull',
            is_delivery_active=True,
            is_pub_active=True,
        )

    def test_07_get_list_after_edit(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert len(data) >= 5

    def test_08_ping(self, client:'ZatoClient') -> 'None':
        pytest.skip('No ping service for pub/sub subscriptions')

    def test_09_delete_one(self, client:'ZatoClient') -> 'None':
        sub_key = self.__class__.created_sub_keys.pop(0)
        _ = client.delete(f'{SERVICE}.delete', sub_key=sub_key)

    def test_10_get_list_after_delete(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_11_delete_rest(self, client:'ZatoClient') -> 'None':
        for sub_key in self.__class__.created_sub_keys[:]:
            _ = client.delete(f'{SERVICE}.delete', sub_key=sub_key)
            self.__class__.created_sub_keys.remove(sub_key)

    def test_12_get_list_final(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)
