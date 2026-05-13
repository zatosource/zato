# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyPI
import pytest

# Local
from _client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_GENERIC_SERVICE = 'zato.generic.connection'
_HTTP_SOAP_SERVICE = 'zato.http-soap'
_TYPE = 'channel-hl7-mllp'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'ZatoClient':
    return ZatoClient(zato_server['host'], zato_server['port'], zato_server['password'])

# ################################################################################################################################
# ################################################################################################################################

def _find_channel_by_name(client:'ZatoClient', name:'str') -> 'dict':
    """ Returns the first MLLP channel matching the given name from the get-list response.
    """
    data, _ = client.get_list(f'{_GENERIC_SERVICE}.get-list', cluster_id=1, type_=_TYPE)

    for item in data:
        if item['name'] == name:
            return item

    raise AssertionError(f'Channel {name!r} not found in get-list response')

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPRestBridgePersistence:
    """ Verifies that use_rest, rest_only, and rest_channel_id survive
    create-read-edit-read round-trips through the generic connection API.
    """

    mllp_id:'int' = 0

# ################################################################################################################################

    def test_01_create_with_rest_fields(self, client:'ZatoClient') -> 'None':
        """ Creates an MLLP channel with use_rest=True, rest_only=False, rest_channel_id=999.
        """

        resp = client.create(f'{_GENERIC_SERVICE}.create',
            cluster_id=1,
            name='test-persist-rest-bridge',
            type_=_TYPE,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            address='127.0.0.1',
            port=18001,
            pool_size=1,
            service='demo.ping',
            use_rest=True,
            rest_only=False,
            rest_channel_id=999,
        )

        assert 'id' in resp
        self.__class__.mllp_id = resp['id']

# ################################################################################################################################

    def test_02_read_back_rest_fields(self, client:'ZatoClient') -> 'None':
        """ Reads the channel back and verifies the REST bridge fields are persisted.
        """

        item = _find_channel_by_name(client, 'test-persist-rest-bridge')

        assert item['use_rest'] is True
        assert item['rest_only'] is False
        assert int(item['rest_channel_id']) == 999

# ################################################################################################################################

    def test_03_edit_to_rest_only(self, client:'ZatoClient') -> 'None':
        """ Edits the channel to set rest_only=True.
        """

        resp = client.edit(f'{_GENERIC_SERVICE}.edit',
            id=self.__class__.mllp_id,
            cluster_id=1,
            name='test-persist-rest-bridge',
            type_=_TYPE,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            address='127.0.0.1',
            port=18001,
            pool_size=1,
            service='demo.ping',
            use_rest=True,
            rest_only=True,
            rest_channel_id=999,
        )

        assert resp['id'] == self.__class__.mllp_id

# ################################################################################################################################

    def test_04_read_back_rest_only(self, client:'ZatoClient') -> 'None':
        """ Reads the channel back and verifies rest_only=True persisted.
        """

        item = _find_channel_by_name(client, 'test-persist-rest-bridge')

        assert item['use_rest'] is True
        assert item['rest_only'] is True
        assert int(item['rest_channel_id']) == 999

# ################################################################################################################################

    def test_05_edit_toggle_off_rest(self, client:'ZatoClient') -> 'None':
        """ Edits the channel to set use_rest=False and clears rest_channel_id.
        """

        resp = client.edit(f'{_GENERIC_SERVICE}.edit',
            id=self.__class__.mllp_id,
            cluster_id=1,
            name='test-persist-rest-bridge',
            type_=_TYPE,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            address='127.0.0.1',
            port=18001,
            pool_size=1,
            service='demo.ping',
            use_rest=False,
            rest_only=False,
            rest_channel_id=0,
        )

        assert resp['id'] == self.__class__.mllp_id

# ################################################################################################################################

    def test_06_read_back_rest_off(self, client:'ZatoClient') -> 'None':
        """ Reads the channel back and verifies use_rest=False and rest_channel_id=0.
        """

        item = _find_channel_by_name(client, 'test-persist-rest-bridge')

        assert item['use_rest'] is False
        assert item['rest_only'] is False
        assert int(item.get('rest_channel_id') or 0) == 0

# ################################################################################################################################

    def test_07_cleanup(self, client:'ZatoClient') -> 'None':
        """ Deletes the test channel.
        """
        client.delete(f'{_GENERIC_SERVICE}.delete', id=self.__class__.mllp_id)

# ################################################################################################################################

    def test_08_verify_deleted(self, client:'ZatoClient') -> 'None':
        """ Verifies the channel no longer appears in the list.
        """
        data, _ = client.get_list(f'{_GENERIC_SERVICE}.get-list', cluster_id=1, type_=_TYPE)
        names = [item['name'] for item in data]
        assert 'test-persist-rest-bridge' not in names

# ################################################################################################################################
# ################################################################################################################################
