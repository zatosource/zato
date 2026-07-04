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
    """Get or create a dedicated security definition for subscriptions."""
    sec_name = 'test-pubsub-sub-sec'
    data, _ = client.get_list('zato.security.basic-auth.get-list', cluster_id=1)
    for item in data:
        if item['name'] == sec_name:
            return item['id']

    response = client.create('zato.security.basic-auth.create',
        cluster_id=1,
        name=sec_name,
        is_active=True,
        username='subtestuser',
        realm='testrealm',
    )
    return response['id']

def _ensure_permission(client:'ZatoClient', sec_base_id:'int') -> 'None':
    """Make sure the security definition can subscribe to the test topics."""
    data, _ = client.get_list('zato.pubsub.permission.get-list', cluster_id=1)
    for item in data:
        if item['sec_base_id'] == sec_base_id and item['pattern'] == 'sub=/test/sub/topic/**':
            return

    _ = client.create('zato.pubsub.permission.create',
        cluster_id=1,
        sec_base_id=sec_base_id,
        pattern='sub=/test/sub/topic/**',
        access_type='publisher-subscriber',
    )

class TestPubSubSubscription:
    created_sub_keys = []
    created_ids = []
    topic_name = None
    sec_id = None

    def test_01_get_list_empty(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_02_create_one(self, client:'ZatoClient') -> 'None':
        self.__class__.topic_name = _ensure_topic(client, '/test/sub/topic/1')
        self.__class__.sec_id = _get_or_create_sec_def(client)
        _ensure_permission(client, self.__class__.sec_id)

        response = client.create(f'{SERVICE}.create',
            cluster_id=1,
            topic_name_list=[self.__class__.topic_name],
            sec_base_id=self.__class__.sec_id,
            delivery_type='pull',
            is_delivery_active=True,
            is_pub_active=True,
        )
        sub_key = response['sub_key']
        assert sub_key
        self.__class__.created_sub_keys.append(sub_key)
        self.__class__.created_ids.append(response['id'])

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
            sub_key = response['sub_key']
            assert sub_key
            self.__class__.created_sub_keys.append(sub_key)
            self.__class__.created_ids.append(response['id'])

    def test_05_get_list_batch(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert len(data) >= 5

    def test_06_edit_one(self, client:'ZatoClient') -> 'None':
        sub_key = self.__class__.created_sub_keys[0]
        _ = client.edit(f'{SERVICE}.edit',
            sub_key=sub_key,
            cluster_id=1,
            # Edit expects a list of dicts, unlike Create which also accepts strings
            topic_name_list=[{
                'topic_name': self.__class__.topic_name,
                'is_pub_enabled': True,
                'is_delivery_enabled': True,
            }],
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
        _ = self.__class__.created_sub_keys.pop(0)
        sub_id = self.__class__.created_ids.pop(0)
        _ = client.delete(f'{SERVICE}.delete', id=sub_id)

    def test_10_get_list_after_delete(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_11_delete_rest(self, client:'ZatoClient') -> 'None':
        for sub_id in self.__class__.created_ids[:]:
            _ = client.delete(f'{SERVICE}.delete', id=sub_id)
            self.__class__.created_ids.remove(sub_id)
        self.__class__.created_sub_keys.clear()

    def test_12_get_list_final(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)
