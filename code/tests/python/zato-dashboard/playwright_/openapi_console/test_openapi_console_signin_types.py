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

from openapi_console_lib import console_login, edit_channel_by_name, relay_invoke, spec_paths, wait_for_spec, \
    Path_Methods, Path_Untyped, Service_Methods, Service_Untyped
from rest_channel import create_apikey_definition, create_bearer_token_definition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.signin.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSigninTypes:
    """ Verifies that callers sign in to the console with any of the credential types
    REST channels support - an API key definition's name and key, and a Bearer token
    definition's client ID and secret - and that filtering and try-it follow that identity.
    """

# ################################################################################################################################

    def test_apikey_signin(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Assigns an API key definition to the untyped channel and signs in to the console
        with the definition's name and its key.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create an API key definition ..
        definition = create_apikey_definition(page, base_url, _Test_Name_Prefix + 'apikey')

        # .. assign it to the untyped channel, which is already active from the earlier tests ..
        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security': f'API key/{definition["name"]}',
        })

        # .. sign in to the console with the definition's name and the key ..
        console_login(page, console_url, definition['name'], definition['key'])

        # .. the caller's document contains exactly the one endpoint the key gives access to ..
        def has_only_untyped_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Untyped}
            return out

        _ = wait_for_spec(page, console_url, has_only_untyped_path)

        # .. and a try-it invocation through the relay runs as that identity.
        response = relay_invoke(page, console_url, 'POST', Path_Untyped, '{}')
        assert response.status == OK, f'Expected OK from the relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == {'echo': True}, f'Unexpected relay response: {data}'

# ################################################################################################################################

    def test_bearer_token_signin(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Assigns a Bearer token definition to the multi-method channel and signs in
        to the console with the definition's client ID and secret.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create a Bearer token definition, whose secret from the create form is stored with it ..
        definition = create_bearer_token_definition(page, base_url, _Test_Name_Prefix + 'bearer')

        # .. assign it to the multi-method channel, which is already active from the earlier tests ..
        _ = edit_channel_by_name(page, base_url, Service_Methods, {
            'security': f'Bearer token/{definition["name"]}',
        })

        # .. sign in to the console with the definition's client ID and secret ..
        console_login(page, console_url, definition['username'], definition['secret'])

        # .. the caller's document contains exactly the one endpoint the definition gives access to ..
        def has_only_methods_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Methods}
            return out

        spec = wait_for_spec(page, console_url, has_only_methods_path)

        # .. both of the service's operations are there ..
        methods = sorted(spec['paths'][Path_Methods])
        assert methods == ['get', 'post'], f'Expected GET and POST, got: {methods}'

        # .. and a try-it invocation through the relay runs as that identity.
        response = relay_invoke(page, console_url, 'GET', Path_Methods)
        assert response.status == OK, f'Expected OK from the relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == {'method': 'GET'}, f'Unexpected relay response: {data}'

# ################################################################################################################################
# ################################################################################################################################
