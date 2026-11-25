# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient
from zato.common.test.conftest_base_pubsub import find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

SERVICE = 'zato.outgoing.amqp'

@pytest.fixture(scope='module')
def client(zato_server:'any_'):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestOutgoingAMQP:
    created_ids = []

    def test_01_get_list_empty(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        assert isinstance(data, list)

    def test_02_create_one(self, client:'any_', amqp_address:'str'):
        resp = client.create(f'{SERVICE}.create',
            name='test-out-amqp-1',
            is_active=True,
            delivery_mode='persistent',
            priority=5,
            pool_size=1,
            address=amqp_address,
            username='guest',
            password='guest',
        )
        assert 'id' in resp
        assert resp['name'] == 'test-out-amqp-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        names = [item['name'] for item in data]
        assert 'test-out-amqp-1' in names

    def test_04_create_batch(self, client:'any_', amqp_address:'str'):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                name=f'test-out-amqp-{i}',
                is_active=True,
                delivery_mode='persistent',
                priority=5,
                pool_size=1,
                address=amqp_address,
                username='guest',
                password='guest',
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        test_items = [item for item in data if item['name'].startswith('test-out-amqp-')]
        assert len(test_items) >= 5

    def test_06_edit_one(self, client:'any_', amqp_address:'str'):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            name='test-out-amqp-1',
            is_active=True,
            delivery_mode='non_persistent',
            priority=3,
            pool_size=2,
            address=amqp_address,
            username='guest',
            password='guest',
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        # The edit does not rename the connection because the AMQP connector registry
        # is keyed by the original name, so we check the edited fields instead.
        edited = [item for item in data if item['name'] == 'test-out-amqp-1']
        assert len(edited) == 1
        assert edited[0]['pool_size'] == 2
        assert edited[0]['priority'] == 3

    def test_08_ping(self, client:'any_'):
        item_id = self.__class__.created_ids[0]
        result = client.invoke(f'{SERVICE}.ping', {'id': item_id})
        assert result['is_success'] is True, result['info']

    def test_08_ping_unreachable_broker(self, client:'any_'):

        # A connection to a port nothing listens on ..
        resp = client.create(f'{SERVICE}.create',
            name='test-out-amqp-unreachable',
            is_active=True,
            delivery_mode='persistent',
            priority=5,
            pool_size=1,
            address=f'amqp://127.0.0.1:{find_free_port()}',
            username='guest',
            password='guest',
        )

        # .. reports the failure of its single connection attempt ..
        try:
            result = client.invoke(f'{SERVICE}.ping', {'id': resp['id']})
            assert result['is_success'] is False
            assert result['info']

        # .. and is deleted whatever the outcome.
        finally:
            client.delete(f'{SERVICE}.delete', id=resp['id'])

    def test_09_delete_one(self, client:'any_'):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        test_items = [item for item in data if item['name'].startswith('test-out-amqp-')]
        assert len(test_items) >= 4

    def test_11_delete_rest(self, client:'any_'):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client:'any_'):
        data, _meta = client.get_list(f'{SERVICE}.get-list')
        test_items = [item for item in data if item['name'].startswith('test-out-amqp-')]
        assert len(test_items) == 0
