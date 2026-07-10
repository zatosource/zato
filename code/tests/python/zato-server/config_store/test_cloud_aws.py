# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient

if 0:
    from zato.common.typing_ import anydict

SERVICE = 'zato.generic.connection'
TYPE = 'cloud-aws'

@pytest.fixture(scope='module')
def client(zato_server:'anydict') -> 'ZatoClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestCloudAWS:
    created_ids = []

    def test_01_get_list_empty(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        assert isinstance(data, list)

    def test_02_create_one(self, client:'ZatoClient') -> 'None':
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-aws-1',
            type_=TYPE,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outgoing=True,
            is_outconn=False,
            region='us-east-1',
            access_key_id='AKIATESTACCESSKEY001',
            endpoint_url='',
            pool_size=1,
        )
        assert 'id' in resp
        assert resp['name'] == 'test-aws-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)

        names = []
        for item in data:
            names.append(item['name'])

        assert 'test-aws-1' in names

    def test_04_create_batch(self, client:'ZatoClient') -> 'None':
        for item_index in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name=f'test-aws-{item_index}',
                type_=TYPE,
                is_active=True,
                is_internal=False,
                is_channel=False,
                is_outgoing=True,
                is_outconn=False,
                region='eu-central-1',
                access_key_id=f'AKIATESTACCESSKEY00{item_index}',
                endpoint_url='',
                pool_size=1,
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)

        test_items = []
        for item in data:
            if item['name'].startswith('test-aws-'):
                test_items.append(item)

        assert len(test_items) >= 5

    def test_06_edit_one(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-aws-1-edited',
            type_=TYPE,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outgoing=True,
            is_outconn=False,
            region='us-west-2',
            access_key_id='AKIATESTACCESSKEY001',
            endpoint_url='',
            pool_size=2,
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)

        names = []
        for item in data:
            names.append(item['name'])

        assert 'test-aws-1-edited' in names
        assert 'test-aws-1' not in names

    def test_08_change_password(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids[0]
        _ = client.invoke(f'{SERVICE}.change-password', {
            'id': item_id,
            'password': 'test-secret-access-key-updated',
            'type_': TYPE,
        })

    def test_09_ping(self, client:'ZatoClient') -> 'None':
        from moto.server import ThreadedMotoServer

        server = ThreadedMotoServer(port=0)
        server.start()
        host, port = server.get_host_and_port()

        try:
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name='test-aws-ping-live',
                type_=TYPE,
                is_active=True,
                is_internal=False,
                is_channel=False,
                is_outgoing=True,
                is_outconn=False,
                region='us-east-1',
                access_key_id='AKIATESTACCESSKEY010',
                endpoint_url=f'http://{host}:{port}',
                secret='test-secret-access-key',
                pool_size=1,
            )
            ping_id = resp['id']
            try:
                result = client.invoke(f'{SERVICE}.ping', {'id': ping_id})
                assert result['is_success'] is True, result['info']
            finally:
                _ = client.delete(f'{SERVICE}.delete', id=ping_id)
        finally:
            server.stop()

    def test_10_delete_one(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids.pop(0)
        _ = client.delete(f'{SERVICE}.delete', id=item_id)

    def test_11_get_list_after_delete(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)

        test_items = []
        for item in data:
            if item['name'].startswith('test-aws-'):
                test_items.append(item)

        assert len(test_items) >= 4

    def test_12_delete_rest(self, client:'ZatoClient') -> 'None':
        for item_id in self.__class__.created_ids[:]:
            _ = client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_13_get_list_final(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)

        test_items = []
        for item in data:
            if item['name'].startswith('test-aws-'):
                test_items.append(item)

        assert len(test_items) == 0
