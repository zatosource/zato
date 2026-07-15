# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import NOT_FOUND

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, relay_invoke, spec_paths, wait_for_spec, \
    Path_Methods, Path_Typed, Path_Untyped, Service_Typed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.relay.' + CryptoManager.generate_hex_string(32) + '.'

# The one body the relay returns for anything the caller cannot reach
_Not_Found_Body = b'Not found'

# A path no channel has ever existed for
_Unknown_Path = '/no/such/path/anywhere'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityRelayEnforcement:
    """ Verifies that the relay rejects endpoints outside the caller's grants with a response
    that is byte-identical to the one for a genuinely unknown path, so nothing is probeable.
    """

# ################################################################################################################################

    def test_relay_enforcement(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Signs in as a user granted one endpoint and invokes another user's endpoint,
        an inactive endpoint and an unknown path through the relay.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # The caller is granted the typed endpoint alone ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'relay')

        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': f'Basic Auth/{definition["name"]}',
        })

        console_login(page, console_url, definition['username'], definition['password'])

        def has_only_typed_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Typed}
            return out

        _ = wait_for_spec(page, console_url, has_only_typed_path)

        # .. another caller's endpoint - active, but not this caller's - is not found ..
        response_other = relay_invoke(page, console_url, 'GET', Path_Methods)
        assert response_other.status == NOT_FOUND, \
            f'Expected 404 for another caller\'s endpoint, got {response_other.status}: {response_other.text()}'

        # .. an inactive endpoint is not found either ..
        response_inactive = relay_invoke(page, console_url, 'GET', Path_Untyped)
        assert response_inactive.status == NOT_FOUND, \
            f'Expected 404 for an inactive endpoint, got {response_inactive.status}: {response_inactive.text()}'

        # .. as is a path that exists for nobody ..
        response_unknown = relay_invoke(page, console_url, 'GET', _Unknown_Path)
        assert response_unknown.status == NOT_FOUND, \
            f'Expected 404 for an unknown path, got {response_unknown.status}: {response_unknown.text()}'

        # .. and all three responses are byte-identical, so none of them is distinguishable.
        body_other = response_other.body()
        body_inactive = response_inactive.body()
        body_unknown = response_unknown.body()

        assert body_other == _Not_Found_Body, f'Unexpected body for another caller\'s endpoint: {body_other}'
        assert body_inactive == _Not_Found_Body, f'Unexpected body for an inactive endpoint: {body_inactive}'
        assert body_unknown == _Not_Found_Body, f'Unexpected body for an unknown path: {body_unknown}'

# ################################################################################################################################
# ################################################################################################################################
