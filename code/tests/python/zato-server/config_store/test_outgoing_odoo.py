# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import time

import pytest
from zato.common.test.client import AdminClient as ZatoClient

SERVICE = 'zato.outgoing.odoo'

@pytest.fixture(scope='module')
def client(zato_server):
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

class TestOutgoingOdoo:
    created_ids = []

    def test_01_get_list_empty(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        assert isinstance(data, list)

    def test_02_create_one(self, client):
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-out-odoo-1',
            is_active=True,
            host='http://localhost',
            port=8069,
            user='admin',
            database='testdb',
            protocol='xmlrpc',
            pool_size=1,
        )
        assert 'id' in resp
        assert resp['name'] == 'test-out-odoo-1'
        self.__class__.created_ids.append(resp['id'])

    def test_03_get_list_after_create(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        names = [item['name'] for item in data]
        assert 'test-out-odoo-1' in names

    def test_04_create_batch(self, client):
        for i in range(2, 6):
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name=f'test-out-odoo-{i}',
                is_active=True,
                host='http://localhost',
                port=8069,
                user='admin',
                database='testdb',
                protocol='xmlrpc',
                pool_size=1,
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_05_get_list_batch(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        test_items = [item for item in data if item['name'].startswith('test-out-odoo-')]
        assert len(test_items) >= 5

    def test_06_edit_one(self, client):
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-out-odoo-1-edited',
            is_active=True,
            host='http://localhost',
            port=8069,
            user='admin',
            database='testdb-edited',
            protocol='xmlrpc',
            pool_size=2,
        )
        assert resp['id'] == item_id

    def test_07_get_list_after_edit(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        names = [item['name'] for item in data]
        assert 'test-out-odoo-1-edited' in names
        assert 'test-out-odoo-1' not in names

    def test_08_ping(self, client):
        import json
        from _ping_stubs import start_http_stub

        def handler(method, path, body_bytes):
            request = json.loads(body_bytes)
            params = request['params']
            service = params['service']
            rpc_method = params['method']

            if service == 'common' and rpc_method in ('login', 'authenticate'):
                result = 1
            elif service == 'object':
                # execute_kw args: (db, uid, password, model, method, args...)
                model_method = params['args'][4]
                if model_method == 'search':
                    result = [1]
                elif model_method == 'read':
                    result = [{'id': 1, 'login': 'admin'}]
                else:
                    result = True
            else:
                result = True

            return {'jsonrpc': '2.0', 'id': request['id'], 'result': result}

        port, server = start_http_stub(handler)
        try:
            resp = client.create(f'{SERVICE}.create',
                cluster_id=1,
                name='test-out-odoo-ping-live',
                is_active=True,
                host='127.0.0.1',
                port=port,
                user='admin',
                password='admin',
                database='testdb',
                protocol='jsonrpc',
                pool_size=1,
            )
            ping_id = resp['id']
            try:
                # The connection queue is built asynchronously so retry until a client is available
                deadline = time.time() + 30
                while True:
                    try:
                        result = client.invoke(f'{SERVICE}.ping', {'id': ping_id})
                    except Exception as e:
                        if 'No free connections' in str(e) and time.time() < deadline:
                            time.sleep(0.25)
                            continue
                        raise
                    else:
                        break
                assert 'Ping OK' in result['info']
            finally:
                client.delete(f'{SERVICE}.delete', id=ping_id)
        finally:
            server.shutdown()

    def test_09_delete_one(self, client):
        item_id = self.__class__.created_ids.pop(0)
        client.delete(f'{SERVICE}.delete', id=item_id)

    def test_10_get_list_after_delete(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        test_items = [item for item in data if item['name'].startswith('test-out-odoo-')]
        assert len(test_items) >= 4

    def test_11_delete_rest(self, client):
        for item_id in self.__class__.created_ids[:]:
            client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

    def test_12_get_list_final(self, client):
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, cur_page=1, paginate=False)
        test_items = [item for item in data if item['name'].startswith('test-out-odoo-')]
        assert len(test_items) == 0
