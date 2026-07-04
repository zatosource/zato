# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient

SERVICE = 'zato.channel.amqp'

@pytest.fixture(scope='module')
def client(zato_server):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestChannelAMQP:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-ch-amqp-1',
            is_active=True,
            address='amqp://localhost:5672',
            username='guest',
            password='guest',
            queue='test-queue-1',
            consumer_tag_prefix='test',
            service='demo.ping',
            pool_size=1,
            ack_mode='ack-after-processing',
            prefetch_count=1,
        )
        assert 'id' in resp
        assert resp['name'] == 'test-ch-amqp-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        names = [item['name'] for item in data]
        assert 'test-ch-amqp-1' in names

    def test_04_create_batch(self, client):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name=f'test-ch-amqp-{i}',
                is_active=True,
                address='amqp://localhost:5672',
                username='guest',
                password='guest',
                queue=f'test-queue-{i}',
                consumer_tag_prefix='test',
                service='demo.ping',
                pool_size=1,
                ack_mode='ack-after-processing',
                prefetch_count=1,
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-ch-amqp-')]
        assert len(test_items) >= 5

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-ch-amqp-1',
            is_active=True,
            address='amqp://localhost:5672',
            username='guest',
            password='guest',
            queue='test-queue-1',
            consumer_tag_prefix='test',
            service='demo.ping',
            pool_size=2,
            ack_mode='ack-after-processing',
            prefetch_count=1,
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        # The edit does not rename the channel because the AMQP connector registry
        # is keyed by the original name, so we only confirm the item is still there.
        edited = [item for item in data if item['name'] == 'test-ch-amqp-1']
        assert len(edited) == 1
        assert edited[0]['pool_size'] == 2

    def test_08_ping(self, client):
        pytest.skip('No ping service for AMQP channels')

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-ch-amqp-')]
        assert len(test_items) >= 4

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        test_items = [item for item in data if item['name'].startswith('test-ch-amqp-')]
        assert len(test_items) == 0
