# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, spec_paths, wait_for_spec, \
    Admin_Username, Path_Untyped, Service_Untyped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.inactive.' + CryptoManager.generate_hex_string(32) + '.'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityInactiveInvisible:
    """ Verifies that deactivating a channel removes it from every document at once,
    the admin's included, with no restart of anything.
    """

# ################################################################################################################################

    # Deactivating a documented endpoint is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_inactive_invisible(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Grants a user the untyped endpoint, confirms visibility, deactivates the channel
        and asserts it is gone from both the user's and the admin's documents.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']
        password = zato_dashboard['password']

        # Give a fresh user the untyped endpoint, which is active at this point ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'inactive')

        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. the user sees the endpoint while the channel is active ..
        console_login(page, console_url, definition['username'], definition['password'])

        def has_only_untyped_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Untyped}
            return out

        _ = wait_for_spec(page, console_url, has_only_untyped_path)

        # .. and so does the admin.
        console_login(page, console_url, Admin_Username, password)

        def has_untyped_path(spec:'anydict') -> 'bool':
            out = Path_Untyped in spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_untyped_path)

        # Deactivate the channel in the Dashboard - nothing is restarted anywhere ..
        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'is_active': False,
        })

        # .. the endpoint drops out of the admin's document ..
        def has_no_untyped_path(spec:'anydict') -> 'bool':
            out = Path_Untyped not in spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_no_untyped_path)

        # .. and the user's document is now empty, since the one grant they have is inactive.
        console_login(page, console_url, definition['username'], definition['password'])

        def has_no_paths(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == set()
            return out

        _ = wait_for_spec(page, console_url, has_no_paths)

# ################################################################################################################################
# ################################################################################################################################
