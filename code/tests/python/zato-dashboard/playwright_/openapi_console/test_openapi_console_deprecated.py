# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, wait_for_spec, \
    Admin_Username, Path_Typed, Service_Typed, Typed_Expected_Response, Typed_Request
from rest_channel import invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.deprecated.' + CryptoManager.generate_hex_string(32) + '.'

# The deprecation attributes the test channel is given
_Deprecation_Sunset = '2030-06-30'
_Deprecation_Successor = '/api/v2/get-user'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleDeprecated:
    """ Verifies that a deprecated channel's endpoint carries deprecated:true in the document,
    with the sunset date and the successor in its description, and that live responses
    announce the Deprecation, Sunset and Link headers.
    """

# ################################################################################################################################

    def test_deprecated_channel(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Deprecates the typed channel and asserts the document and the live traffic
        both announce the deprecation, then reverts the channel.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']
        server_port = zato_dashboard['server_port']
        password = zato_dashboard['password']

        # The channel is active and secured with this test's own definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'deprecated')

        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. the endpoint carries no deprecation information while the flag is off ..
        console_login(page, console_url, Admin_Username, password)

        def has_regular_operation(spec:'anydict') -> 'bool':
            operation = spec['paths'][Path_Typed]['post']
            out = 'deprecated' not in operation
            return out

        _ = wait_for_spec(page, console_url, has_regular_operation)

        # Deprecate the channel in the Dashboard, with a sunset date and a successor ..
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'is_deprecated': True,
            'deprecation_sunset': _Deprecation_Sunset,
            'deprecation_successor': _Deprecation_Successor,
        })

        # .. the operation is marked as deprecated in the document itself ..
        def has_deprecated_operation(spec:'anydict') -> 'bool':
            operation = spec['paths'][Path_Typed]['post']
            out = operation.get('deprecated') is True
            return out

        spec = wait_for_spec(page, console_url, has_deprecated_operation)

        # .. and its description points callers to the sunset date and the successor.
        description = spec['paths'][Path_Typed]['post']['description']
        assert _Deprecation_Sunset in description, f'Expected the sunset date in the description: {description}'
        assert _Deprecation_Successor in description, f'Expected the successor in the description: {description}'

        # The channel keeps serving - deprecation is a signal, not a switch ..
        response = invoke_until_status(
            server_port, Path_Typed, OK,
            json_data=Typed_Request,
            auth=(definition['username'], definition['password']),
        )

        assert response.status_code == OK, f'Expected OK from the channel, got {response.status_code}: {response.text}'

        data = response.json()
        assert data == Typed_Expected_Response, f'Unexpected channel response: {data}'

        # .. and every response announces the deprecation headers.
        assert response.headers['Deprecation'].startswith('@'), f'Unexpected Deprecation header: {response.headers}'
        assert '2030' in response.headers['Sunset'], f'Unexpected Sunset header: {response.headers}'
        assert _Deprecation_Successor in response.headers['Link'], f'Unexpected Link header: {response.headers}'
        assert 'successor-version' in response.headers['Link'], f'Unexpected Link header: {response.headers}'

        # Revert the deprecation so the channel is a regular one again for any later test.
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'is_deprecated': False,
        })

        _ = wait_for_spec(page, console_url, has_regular_operation)

# ################################################################################################################################
# ################################################################################################################################
