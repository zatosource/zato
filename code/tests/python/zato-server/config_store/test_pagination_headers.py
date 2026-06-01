# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# Local
from _client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

SERVICE = 'zato.security.basic-auth'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server):
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

# ################################################################################################################################
# ################################################################################################################################

class TestPaginationHeaders:

    created_ids = []

    def test_01_create_items_for_pagination(self, client):
        """ Create enough items so that pagination has something to paginate.
        """
        for idx in range(1, 6):
            resp = client.create(f'{SERVICE}.create',
                name=f'test-pagination-{idx}',
                is_active=True,
                username=f'pag-user-{idx}',
                realm='pag-realm',
            )
            assert 'id' in resp
            self.__class__.created_ids.append(resp['id'])

    def test_02_get_list_returns_bare_list_with_pagination_headers(self, client):
        """ Invoke get-list with paginate=True, assert body is a bare list
        and pagination headers are present.
        """
        response, headers = client._invoke(f'{SERVICE}.get-list', {
            'cluster_id': 1,
            'paginate': True,
            'cur_page': 1,
        })

        # .. the response body must be a bare list ..
        assert isinstance(response, list), f'Expected list, got {type(response).__name__}'

        # .. pagination headers must be present ..
        assert 'X-Zato-Page-Current' in headers, f'Missing X-Zato-Page-Current, headers: {headers}'
        assert 'X-Zato-Page-Size' in headers, f'Missing X-Zato-Page-Size, headers: {headers}'
        assert 'X-Zato-Page-Total' in headers, f'Missing X-Zato-Page-Total, headers: {headers}'
        assert 'X-Zato-Result-Total' in headers, f'Missing X-Zato-Result-Total, headers: {headers}'
        assert 'X-Zato-Page-Has-Next' in headers, f'Missing X-Zato-Page-Has-Next, headers: {headers}'
        assert 'X-Zato-Page-Has-Previous' in headers, f'Missing X-Zato-Page-Has-Previous, headers: {headers}'

        # .. the total must be at least the number of items we created ..
        total = int(headers['X-Zato-Result-Total'])
        assert total >= 5

    def test_03_get_list_no_meta_in_body(self, client):
        """ Verify that the response body does NOT contain _meta or response wrapper keys.
        """
        response, headers = client._invoke(f'{SERVICE}.get-list', {
            'cluster_id': 1,
            'paginate': True,
            'cur_page': 1,
        })

        # .. if response is a dict, it must not have _meta ..
        if isinstance(response, dict):
            assert '_meta' not in response, 'Body should not contain _meta'
            assert 'response' not in response, 'Body should not contain response wrapper'

    def test_04_get_list_helper_returns_meta_from_headers(self, client):
        """ Verify that the get_list() helper populates meta from headers.
        """
        data, meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1, paginate=True, cur_page=1)

        assert isinstance(data, list)
        assert 'cur_page' in meta
        assert 'total' in meta
        assert int(meta['total']) >= 5

    def test_99_cleanup(self, client):
        """ Remove all items created during the test.
        """
        for item_id in self.__class__.created_ids:
            client.delete(f'{SERVICE}.delete', id=item_id)

# ################################################################################################################################
# ################################################################################################################################
