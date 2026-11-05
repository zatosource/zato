# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import loads

# Zato
from zato.common.crypto.api import CryptoManager

from api_portal_lib import portal_login_api_key, edit_channel_by_name, relay_invoke, spec_paths, wait_for_spec
from rest_channel import create_apikey_definition, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.values.' + CryptoManager.generate_hex_string(32) + '.'

_Service_Values = 'api.test.openapi.values.orders'
_Path_Values    = '/api/test/openapi/values/orders'

# What the fixture service's values look like once serialized
_Created_ISO = '2026-01-02T03:04:05'
_Amount_Text = '1.10'

# ################################################################################################################################
# ################################################################################################################################

class TestAPIPortalTypedValues:
    """ Verifies that try-it relays responses carrying dates, decimal numbers and lists of models,
    with the same body that the REST channel itself responds with.
    """

# ################################################################################################################################

    def test_values_are_relayed_as_the_rest_channel_sends_them(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Secures the values channel with a new API key, invokes it directly and through the relay,
        and compares the two bodies for GET and for POST.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        portal_url = zato_dashboard['portal_url']
        server_port = zato_dashboard['server_port']

        # Create an API key definition ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'key')
        key_headers = {definition['header']: definition['key']}

        # .. secure the values channel with it and activate the channel ..
        _ = edit_channel_by_name(page, base_url, _Service_Values, {
            'security': f'API key/{definition["name"]}',
            'is_active': True,
        })

        # .. invoke the channel directly, which is what the relay must reproduce ..
        rest_get = invoke_until_status(server_port, _Path_Values, OK, method='GET', headers=key_headers)
        assert rest_get.status_code == OK, f'Expected OK from the channel for GET, got {rest_get.status_code}: {rest_get.text}'

        rest_post = invoke_until_status(server_port, _Path_Values, OK, method='POST', json_data={}, headers=key_headers)
        assert rest_post.status_code == OK, f'Expected OK from the channel for POST, got {rest_post.status_code}: {rest_post.text}'

        # .. sign in to the portal with the key ..
        portal_login_api_key(page, portal_url, definition['key'])

        def has_values_path(spec:'anydict') -> 'bool':
            out = _Path_Values in spec_paths(spec)
            return out

        _ = wait_for_spec(page, portal_url, has_values_path)

        # .. the date and the decimal number arrive through the relay ..
        relay_get = relay_invoke(page, portal_url, 'GET', _Path_Values)
        assert relay_get.status == OK, f'Expected OK from the relay for GET, got {relay_get.status}: {relay_get.text()}'

        data = loads(relay_get.text())
        assert data == {'created': _Created_ISO, 'amount': _Amount_Text}, f'Unexpected relay response for GET: {data}'

        # .. exactly as the channel sends them ..
        assert relay_get.text() == rest_get.text, f'Relay body `{relay_get.text()}` differs from channel body `{rest_get.text}`'

        # .. and so does the list of models.
        relay_post = relay_invoke(page, portal_url, 'POST', _Path_Values, '{}')
        assert relay_post.status == OK, f'Expected OK from the relay for POST, got {relay_post.status}: {relay_post.text()}'

        data = loads(relay_post.text())
        expected = [
            {'order_id': 1, 'created': _Created_ISO},
            {'order_id': 2, 'created': _Created_ISO},
        ]
        assert data == expected, f'Unexpected relay response for POST: {data}'

        assert relay_post.text() == rest_post.text, \
            f'Relay body `{relay_post.text()}` differs from channel body `{rest_post.text}`'

# ################################################################################################################################
# ################################################################################################################################
