# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, spec_paths, wait_for_spec, \
    Path_Methods, Path_Typed, Service_Methods, Service_Typed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.methods.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleMethods:
    """ Verifies that per-verb handlers become one documented operation each,
    while a service with only a handle method is documented as POST alone.
    """

# ################################################################################################################################

    def test_http_methods(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Grants a user the multi-method and the typed endpoints and asserts their operations.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # One definition grants both endpoints ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'methods')
        security_label = f'Basic Auth/{definition["name"]}'

        # .. the multi-method channel gets activated and secured ..
        _ = edit_channel_by_name(page, base_url, Service_Methods, {
            'is_active': True,
            'security': security_label,
        })

        # .. and the already active typed channel is switched over to the same definition ..
        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': security_label,
        })

        # .. sign in to the console as that user ..
        console_login(page, console_url, definition['username'], definition['password'])

        # .. the document contains exactly the two granted endpoints ..
        def has_both_paths(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Methods, Path_Typed}
            return out

        spec = wait_for_spec(page, console_url, has_both_paths)

        # .. the service with handle_GET and handle_POST is documented with both operations ..
        methods = sorted(spec['paths'][Path_Methods])
        assert methods == ['get', 'post'], f'Expected GET and POST, got: {methods}'

        # .. and the service with only a handle method is documented as POST alone.
        methods = list(spec['paths'][Path_Typed])
        assert methods == ['post'], f'Expected only POST, got: {methods}'

# ################################################################################################################################
# ################################################################################################################################
