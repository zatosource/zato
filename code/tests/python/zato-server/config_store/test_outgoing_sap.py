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

class TestOutgoingSAP:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        response = client.create(f'{SERVICE}.create',
            name='test-sap-1',
            is_active=True,
            type_='outconn-sap',
            address='https://sap.example.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/',
            odata_version='2.0',
            auth_type='basic',
            username='api.user',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert 'id' in response
        assert response['name'] == 'test-sap-1'
        self.__class__.created_ids.append(response['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-sap-1' in names

    def test_04_sap_does_not_appear_in_odata_list(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-odata')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-sap-1' not in names

    def test_05_opaque_fields_round_trip(self, client):
        response = client.create(f'{SERVICE}.create',
            name='test-sap-opaque',
            is_active=True,
            type_='outconn-sap',
            address='https://api4.successfactors.com/odata/v2/',
            odata_version='2.0',
            auth_type='oauth2',
            token_url='https://api4.successfactors.com/oauth/token',
            tenant_id='test-company',
            client_id='test-client-id',
            needs_csrf_token=True,
            page_size=100,
            timeout=30,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert 'id' in response
        self.__class__.created_ids.append(response['id'])

        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        found = None

        for item in data:
            if item['name'] == 'test-sap-opaque':
                found = item
                break

        assert found is not None
        assert found['odata_version'] == '2.0'
        assert found['auth_type'] == 'oauth2'
        assert found['token_url'] == 'https://api4.successfactors.com/oauth/token'
        assert found['tenant_id'] == 'test-company'
        assert found['client_id'] == 'test-client-id'

    def test_06_create_batch(self, client):
        for number in range(2, 6):
            response = client.create(f'{SERVICE}.create',
                name=f'test-sap-{number}',
                is_active=True,
                type_='outconn-sap',
                address=f'https://sap{number}.example.com/sap/opu/odata/',
                odata_version='2.0',
                auth_type='basic',
                is_internal=False,
                is_channel=False,
                is_outconn=True,
            )
            assert 'id' in response
            self.__class__.created_ids.append(response['id'])

    def test_07_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        test_items = []

        for item in data:
            if item['name'].startswith('test-sap-'):
                test_items.append(item)

        assert len(test_items) >= 6

    def test_08_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-sap-1-edited',
            is_active=True,
            type_='outconn-sap',
            address='https://sap-edited.example.com/sap/opu/odata/',
            odata_version='2.0',
            auth_type='bearer',
            is_internal=False,
            is_channel=False,
            is_outconn=True,
        )
        assert response['id'] == item_id

    def test_09_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        names = []

        for item in data:
            names.append(item['name'])

        assert 'test-sap-1-edited' in names
        assert 'test-sap-1' not in names

    def test_10_change_password(self, client):
        item_id = self.__class__.created_ids[0]
        response = client.invoke(f'{SERVICE}.change-password', {
            'id': item_id,
            'password': 'new-sap-secret',
        })
        assert response is not None

    def test_11_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_12_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        test_items = []

        for item in data:
            if item['name'].startswith('test-sap-'):
                test_items.append(item)

        assert len(test_items) >= 5

    def test_13_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_14_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_='outconn-sap')
        test_items = []

        for item in data:
            if item['name'].startswith('test-sap-'):
                test_items.append(item)

        assert len(test_items) == 0
