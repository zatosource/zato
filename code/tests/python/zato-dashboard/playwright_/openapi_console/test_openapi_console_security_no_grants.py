# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FOUND, OK

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, get_spec_response, Console_Login_Path, Path_Diffing, Path_Methods, \
    Path_Typed, Path_Untyped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.nogrants.' + CryptoManager.generate_hex_string(32) + '.'

# None of these may appear in the document of a user with no grants
_Fixture_Names = [
    Path_Typed,
    Path_Untyped,
    Path_Methods,
    Path_Diffing,
    'GetUserRequest',
    'GetUserResponse',
    'ContractResponse',
]

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityNoGrants:
    """ Verifies that valid credentials with no grants establish a session and receive
    an empty document - grants shape the document, never the sign-in itself.
    """

# ################################################################################################################################

    def test_no_grants(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a user assigned to no channel, signs in and asserts the empty document.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create a definition that no channel and no group references ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'ungrant')

        # .. the first sign-in also waits out the propagation of the new definition ..
        console_login(page, console_url, definition['username'], definition['password'])

        # .. and now the sign-in POST itself demonstrably redirects to the console page.
        _ = page.goto(console_url + Console_Login_Path)

        page.fill('#username', definition['username'])
        page.fill('#password', definition['password'])

        def is_login_post(response:'any_') -> 'bool':
            out = response.url.endswith(Console_Login_Path) and response.request.method == 'POST'
            return out

        with page.expect_response(is_login_post) as response_info:
            page.click('.console-login-button')

        response = response_info.value
        assert response.status == FOUND, f'Expected a redirect after a valid sign-in, got {response.status}'

        # The user's document is a well-formed one with nothing in it ..
        response = get_spec_response(page, console_url)
        body = response.text()

        assert response.status == OK, f'Expected OK from the document endpoint, got {response.status}: {body}'

        spec = response.json()
        assert spec['paths'] == {}, f'Expected no paths, got: {sorted(spec["paths"])}'
        assert spec['components']['schemas'] == {}, f'Expected no schemas, got: {sorted(spec["components"]["schemas"])}'

        # .. and no fixture path or schema name appears anywhere in the body.
        for fixture_name in _Fixture_Names:
            assert fixture_name not in body, f'`{fixture_name}` leaked into the empty document: {body}'

# ################################################################################################################################
# ################################################################################################################################
