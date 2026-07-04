# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import time

import pytest
from zato.common.test.client import AdminClient as ZatoClient

SERVICE = 'zato.generic.connection'
TYPE = 'outconn-ldap'

@pytest.fixture(scope='module')
def client(zato_server):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestOutgoingLDAP:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-out-ldap-1',
            type_=TYPE,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address='ldap://localhost:389',
            username='cn=admin,dc=test,dc=com',
            pool_size=1,
            pool_max_cycles=1,
            pool_keep_alive=30,
            use_auto_range=True,
            use_tls=False,
            sasl_mechanism='',
            server_list='ldap://localhost:389',
        )
        assert 'id' in resp
        assert resp['name'] == 'test-out-ldap-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        names = [item['name'] for item in data]
        assert 'test-out-ldap-1' in names

    def test_04_create_batch(self, client):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name=f'test-out-ldap-{i}',
                type_=TYPE,
                is_active=True,
                is_internal=False,
                is_channel=False,
                is_outconn=True,
                address='ldap://localhost:389',
                username=f'cn=admin{i},dc=test,dc=com',
                pool_size=1,
                pool_max_cycles=1,
                pool_keep_alive=30,
                use_auto_range=True,
                use_tls=False,
                sasl_mechanism='',
                server_list='ldap://localhost:389',
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        test_items = [item for item in data if item['name'].startswith('test-out-ldap-')]
        assert len(test_items) >= 5

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-out-ldap-1-edited',
            type_=TYPE,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address='ldap://localhost:389',
            username='cn=admin,dc=test,dc=com',
            pool_size=2,
            pool_max_cycles=1,
            pool_keep_alive=30,
            use_auto_range=True,
            use_tls=False,
            sasl_mechanism='',
            server_list='ldap://localhost:389',
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        names = [item['name'] for item in data]
        assert 'test-out-ldap-1-edited' in names
        assert 'test-out-ldap-1' not in names

    def test_08_ping(self, client):
        from _ping_stubs import start_ldap_stub
        port, server = start_ldap_stub()
        try:
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name='test-out-ldap-ping-live',
                type_=TYPE,
                is_active=True,
                is_internal=False,
                is_channel=False,
                is_outconn=True,
                address=f'ldap://127.0.0.1:{port}',
                username='cn=admin,dc=test,dc=com',
                password='test-password',
                pool_size=1,
                pool_max_cycles=1,
                pool_keep_alive=30,
                use_auto_range=True,
                use_tls=False,
                sasl_mechanism='',
                server_list=f'ldap://127.0.0.1:{port}',
                is_tls_enabled=False,
                get_info='NO_INFO',
                connect_timeout=5,
                ip_mode='IP_SYSTEM_DEFAULT',
                pool_ha_strategy='ROUND_ROBIN',
                pool_exhaust_timeout=5,
                auto_bind=False,
                should_check_names=True,
                is_read_only=False,
                pool_name='',
                pool_lifetime=30,
                should_return_empty_attrs=True,
            )
            ping_id = resp['id']
            try:
                # The connection queue is built asynchronously so retry until a client is available
                deadline = time.time() + 30
                while True:
                    result = client.invoke('zato.generic.connection.ping', {'id': ping_id})
                    if not result['is_success'] and 'No free connections' in result['info'] and time.time() < deadline:
                        time.sleep(0.25)
                        continue
                    break
                assert result['is_success'] is True, result['info']
            finally:
                client.delete(f'{SERVICE}.delete', id=ping_id)
        finally:
            server.shutdown()

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        test_items = [item for item in data if item['name'].startswith('test-out-ldap-')]
        assert len(test_items) >= 4

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, type_=TYPE)
        test_items = [item for item in data if item['name'].startswith('test-out-ldap-')]
        assert len(test_items) == 0
