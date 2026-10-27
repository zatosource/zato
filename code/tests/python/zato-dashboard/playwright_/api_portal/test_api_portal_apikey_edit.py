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

from api_portal_lib import portal_login_api_key, edit_channel_by_name, relay_invoke, spec_paths, wait_for_spec, \
    Path_Untyped, Service_Untyped
from rest_channel import create_apikey_definition, invoke_until_status
from security_edit import rename_apikey_definition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.apikey-edit.' + CryptoManager.generate_hex_string(32) + '.'

# What the untyped fixture service replies with
_Echo_Response = {'echo': True}

# ################################################################################################################################
# ################################################################################################################################

class TestAPIPortalAPIKeyEdit:
    """ Verifies that an API key edited in the Dashboard keeps its key - the portal still accepts it
    for sign-in and try-it, and the REST channel it secures still accepts it too.
    """

# ################################################################################################################################

    def test_apikey_works_after_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Secures the untyped channel with a new API key, renames the key in the Dashboard
        and checks that the key is accepted everywhere it was accepted before the edit.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        portal_url = zato_dashboard['portal_url']
        server_port = zato_dashboard['server_port']

        # Create an API key definition ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'before')
        key_headers = {definition['header']: definition['key']}

        # .. and secure the untyped channel with it ..
        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security': f'API key/{definition["name"]}',
            'is_active': True,
        })

        # .. the channel accepts the key before the edit ..
        response = invoke_until_status(server_port, Path_Untyped, OK, json_data={}, headers=key_headers)
        assert response.status_code == OK, f'Expected OK from the channel before the edit, got {response.status_code}'

        # .. now rename the definition, which leaves its key as it was ..
        rename_apikey_definition(page, base_url, definition['name'], _Test_Name_Prefix + 'after')

        # .. the channel still accepts the key ..
        response = invoke_until_status(server_port, Path_Untyped, OK, json_data={}, headers=key_headers)
        assert response.status_code == OK, \
            f'Expected OK from the channel after the edit, got {response.status_code}: {response.text}'

        # .. the portal still accepts it for sign-in ..
        portal_login_api_key(page, portal_url, definition['key'])

        # .. the caller's document contains the endpoint the key gives access to ..
        def has_untyped_path(spec:'anydict') -> 'bool':
            out = Path_Untyped in spec_paths(spec)
            return out

        _ = wait_for_spec(page, portal_url, has_untyped_path)

        # .. and a try-it invocation through the relay runs as that identity.
        response = relay_invoke(page, portal_url, 'POST', Path_Untyped, '{}')
        assert response.status == OK, f'Expected OK from the relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == _Echo_Response, f'Unexpected relay response: {data}'

# ################################################################################################################################
# ################################################################################################################################
