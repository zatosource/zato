# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from _client import ZatoClient

SERVICE = 'zato.generic.connection'

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

class TestOutgoingGraphQL:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        response = client.create(f'{SERVICE}.create',
            name='test-graphql-1',
            is_active=True,
            type_='outconn-graphql',
            address='https://graphql.example.com/api',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            pool_size=1,
        )
        assert 'id' in response
        assert response['name'] == 'test-graphql-1'
        self.__class__.created_ids.append(response['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-graphql-1' in names

    def test_04_create_batch(self, client):
        for number in range(2, 6):
            response = client.create(f'{SERVICE}.create',
                name=f'test-graphql-{number}',
                is_active=True,
                type_='outconn-graphql',
                address=f'https://graphql{number}.example.com/api',
                is_internal=False,
                is_channel=False,
                is_outconn=True,
                pool_size=1,
            )
            assert 'id' in response
            self.__class__.created_ids.append(response['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        test_items = []

        for item in data:
            if item['name'].startswith('test-graphql-'):
                test_items.append(item)

        assert len(test_items) >= 5

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.edit(f'{SERVICE}.edit',
            id=item_id,
            name='test-graphql-1-edited',
            is_active=True,
            type_='outconn-graphql',
            address='https://graphql-edited.example.com/api',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            pool_size=1,
        )
        assert response['id'] == item_id

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-graphql-1-edited' in names
        assert 'test-graphql-1' not in names

    def test_08_ping(self, client):
        pytest.skip('Ping requires a live GraphQL server')

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        test_items = []

        for item in data:
            if item['name'].startswith('test-graphql-'):
                test_items.append(item)

        assert len(test_items) >= 4

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-graphql')
        test_items = []

        for item in data:
            if item['name'].startswith('test-graphql-'):
                test_items.append(item)

        assert len(test_items) == 0
