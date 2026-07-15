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
    Any_Object_Schema, Path_Untyped, Service_Untyped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.untyped.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleUntypedSchema:
    """ Verifies that a service without typed input or output is documented
    with the default any-JSON-object schema in both directions.
    """

# ################################################################################################################################

    def test_untyped_service_schema(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Grants a user the untyped echo endpoint and asserts its request and response schemas.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create a Basic Auth definition and grant it the untyped endpoint ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'untyped')

        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'is_active': True,
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. sign in to the console as that user ..
        console_login(page, console_url, definition['username'], definition['password'])

        # .. the document contains only the untyped endpoint ..
        def has_only_untyped_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Untyped}
            return out

        spec = wait_for_spec(page, console_url, has_only_untyped_path)

        # .. the request body accepts any JSON object ..
        operation = spec['paths'][Path_Untyped]['post']

        request_schema = operation['requestBody']['content']['application/json']['schema']
        assert request_schema == Any_Object_Schema, f'Unexpected request schema: {request_schema}'

        # .. the response is any JSON object too ..
        response_schema = operation['responses']['200']['content']['application/json']['schema']
        assert response_schema == Any_Object_Schema, f'Unexpected response schema: {response_schema}'

        # .. and no component schemas exist because nothing references any.
        schemas = spec['components']['schemas']
        assert schemas == {}, f'Expected no component schemas, got: {sorted(schemas)}'

# ################################################################################################################################
# ################################################################################################################################
