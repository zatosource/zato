# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import dumps, loads

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, relay_invoke, spec_paths, wait_for_spec, \
    Path_Typed, Service_Typed, Typed_Expected_Response, Typed_Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.access.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleActivationAccess:
    """ Verifies the full path from an inactive auto-created channel to a working endpoint -
    activation and security assignment in the Dashboard, per-caller document filtering
    in the console and a try-it invocation through the relay.
    """

# ################################################################################################################################

    def test_activation_and_access(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Activates the typed service's channel, assigns a Basic Auth definition to it,
        signs in to the console as that user and invokes the endpoint through the relay.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create a Basic Auth definition for the caller ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'typed')

        # .. activate the auto-created channel and assign the definition to it in one edit ..
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'is_active': True,
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. sign in to the console as that user ..
        console_login(page, console_url, definition['username'], definition['password'])

        # .. the caller's document contains exactly the one endpoint the definition gives access to ..
        def has_only_typed_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Typed}
            return out

        spec = wait_for_spec(page, console_url, has_only_typed_path)

        # .. the service has only a handle method, so the endpoint is documented as POST alone ..
        methods = list(spec['paths'][Path_Typed])
        assert methods == ['post'], f'Expected only POST, got: {methods}'

        # .. and a try-it invocation through the relay returns the service's deterministic response.
        body = dumps(Typed_Request)
        response = relay_invoke(page, console_url, 'POST', Path_Typed, body)

        assert response.status == OK, f'Expected OK from the relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == Typed_Expected_Response, f'Unexpected relay response: {data}'

# ################################################################################################################################
# ################################################################################################################################
