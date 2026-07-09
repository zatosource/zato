# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import pytest
from zato.common.test.client import AdminClient as ZatoClient

SERVICE = 'zato.generic.connection'

@pytest.fixture(scope='module')
def client(zato_server):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestOutgoingOData:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        response = client.create(f'{SERVICE}.create',
            name='test-odata-1',
            is_active=True,
            type_='outconn-odata',
            address='https://odata.example.com/v2.0/tenant/production/api/v2.0/',
            odata_version='4.0',
            auth_type='basic',
            username='api.user',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert 'id' in response
        assert response['name'] == 'test-odata-1'
        self.__class__.created_ids.append(response['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-odata-1' in names

    def test_04_opaque_fields_round_trip(self, client):
        response = client.create(f'{SERVICE}.create',
            name='test-odata-opaque',
            is_active=True,
            type_='outconn-odata',
            address='https://odata.example.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/',
            odata_version='2.0',
            auth_type='oauth2',
            token_url='https://login.example.com/tenant/oauth2/v2.0/token',
            tenant_id='test-tenant',
            client_id='test-client-id',
            scopes='https://api.example.com/.default',
            needs_csrf_token=True,
            page_size=100,
            timeout=30,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert 'id' in response
        self.__class__.created_ids.append(response['id'])

        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        found = None

        for item in data:
            if item['name'] == 'test-odata-opaque':
                found = item
                break

        assert found is not None
        assert found['odata_version'] == '2.0'
        assert found['auth_type'] == 'oauth2'
        assert found['token_url'] == 'https://login.example.com/tenant/oauth2/v2.0/token'
        assert found['tenant_id'] == 'test-tenant'
        assert found['client_id'] == 'test-client-id'
        assert found['scopes'] == 'https://api.example.com/.default'

    def test_05_create_batch(self, client):
        for number in range(2, 6):
            response = client.create(f'{SERVICE}.create',
                name=f'test-odata-{number}',
                is_active=True,
                type_='outconn-odata',
                address=f'https://odata{number}.example.com/data/',
                odata_version='4.0',
                auth_type='basic',
                is_internal=False,
                is_channel=False,
                is_outconn=True,
            )
            assert 'id' in response
            self.__class__.created_ids.append(response['id'])

    def test_06_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        test_items = []

        for item in data:
            if item['name'].startswith('test-odata-'):
                test_items.append(item)

        assert len(test_items) >= 6

    def test_07_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-odata-1-edited',
            is_active=True,
            type_='outconn-odata',
            address='https://odata-edited.example.com/data/',
            odata_version='4.0',
            auth_type='bearer',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert response['id'] == item_id

    def test_08_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-odata-1-edited' in names
        assert 'test-odata-1' not in names

    def test_09_change_password(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{SERVICE}.change-password', {
            'id': item_id,
            'password': 'new-odata-secret',
        })
        assert response is not None

    def test_10_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_11_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        test_items = []

        for item in data:
            if item['name'].startswith('test-odata-'):
                test_items.append(item)

        assert len(test_items) >= 5

    def test_12_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_13_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        test_items = []

        for item in data:
            if item['name'].startswith('test-odata-'):
                test_items.append(item)

        assert len(test_items) == 0
