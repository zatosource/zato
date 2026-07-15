# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import dumps, loads

from openapi_console_lib import console_login, relay_invoke, spec_paths, wait_for_spec, \
    Admin_Username, Path_Prestarted, Path_Typed, Typed_Expected_Response, Typed_Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleAdminView:
    """ Verifies that the admin account sees every active endpoint regardless of security
    assignments and that the admin can invoke any of them through the relay.
    """

# ################################################################################################################################

    def test_admin_sees_all_active_endpoints(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Signs in to the console as admin and asserts the document and the relay
        cover both a secured and an open endpoint.
        """
        page = logged_in_page
        console_url = zato_dashboard['console_url']
        password = zato_dashboard['password']

        # Sign in to the console with the environment's admin credentials ..
        console_login(page, console_url, Admin_Username, password)

        # .. the admin document carries every active endpoint - the secured typed one
        # and the open prestarted one alike ..
        def has_all_active_paths(spec:'anydict') -> 'bool':
            out = {Path_Typed, Path_Prestarted} <= spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_all_active_paths)

        # .. a try-it invocation of the open endpoint returns its response ..
        response = relay_invoke(page, console_url, 'POST', Path_Prestarted, '{}')
        assert response.status == OK, f'Expected OK from the ping relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == {'ping': 'pong'}, f'Unexpected ping response: {data}'

        # .. and the admin invokes the secured endpoint too, with no channel-specific credentials.
        body = dumps(Typed_Request)
        response = relay_invoke(page, console_url, 'POST', Path_Typed, body)
        assert response.status == OK, f'Expected OK from the typed relay, got {response.status}: {response.text()}'

        data = loads(response.text())
        assert data == Typed_Expected_Response, f'Unexpected typed response: {data}'

# ################################################################################################################################
# ################################################################################################################################
