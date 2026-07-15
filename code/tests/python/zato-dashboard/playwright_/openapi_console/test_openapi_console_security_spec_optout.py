# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, spec_paths, wait_for_spec, \
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

_Test_Name_Prefix = 'test.openapi.optout.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecuritySpecOptout:
    """ Verifies that unchecking a channel's OpenAPI flag removes the endpoint from every
    document, the admin's included, while the channel itself keeps serving traffic.
    """

# ################################################################################################################################

    # Opting a documented endpoint out is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_spec_optout(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Opts the typed channel out of OpenAPI documents and asserts the document
        and the live traffic go their separate ways.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']
        server_port = zato_dashboard['server_port']
        password = zato_dashboard['password']

        # The channel is active and secured with this test's own definition ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'optout')

        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. the admin sees the endpoint while the flag is on ..
        console_login(page, console_url, Admin_Username, password)

        def has_typed_path(spec:'anydict') -> 'bool':
            out = Path_Typed in spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_typed_path)

        # Uncheck the OpenAPI flag in the Dashboard ..
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'should_include_in_openapi': False,
        })

        # .. the endpoint drops out of the admin's document ..
        def has_no_typed_path(spec:'anydict') -> 'bool':
            out = Path_Typed not in spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_no_typed_path)

        # .. and out of the granted user's document too.
        console_login(page, console_url, definition['username'], definition['password'])

        def has_no_paths(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == set()
            return out

        _ = wait_for_spec(page, console_url, has_no_paths)

        # The channel itself keeps serving - the flag shapes the document only, never the traffic.
        response = invoke_until_status(
            server_port, Path_Typed, OK,
            json_data=Typed_Request,
            auth=(definition['username'], definition['password']),
        )

        assert response.status_code == OK, f'Expected OK from the channel, got {response.status_code}: {response.text}'

        data = response.json()
        assert data == Typed_Expected_Response, f'Unexpected channel response: {data}'

        # Turn the flag back on so the channel is documented again for any later test.
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'should_include_in_openapi': True,
        })

        console_login(page, console_url, Admin_Username, password)
        _ = wait_for_spec(page, console_url, has_typed_path)

# ################################################################################################################################
# ################################################################################################################################
