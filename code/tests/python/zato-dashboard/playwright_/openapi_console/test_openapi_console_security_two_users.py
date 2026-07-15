# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_basic_auth

from openapi_console_lib import console_login, edit_channel_by_name, get_spec_yaml, spec_paths, spec_schema_names, \
    wait_for_spec, Path_Typed, Path_Untyped, Service_Typed, Service_Untyped, Spec_YAML_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.openapi.twousers.' + CryptoManager.generate_hex_string(32) + '.'

# The schemas only the typed endpoint uses - they belong to user A alone
_Typed_Schema_Names = ['Address', 'GetUserRequest', 'GetUserResponse']

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityTwoUsers:
    """ Verifies that two users with different grants receive disjoint documents
    and that neither one's paths or schemas leak into the other's, in JSON and in YAML.
    """

# ################################################################################################################################

    def test_two_users(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Grants user A the typed endpoint and user B the untyped one, then checks
        both documents for cross-user leaks.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']

        # Create the two users and give each their own endpoint ..
        definition_a = create_basic_auth(page, base_url, _Test_Name_Prefix, 'user-a')
        definition_b = create_basic_auth(page, base_url, _Test_Name_Prefix, 'user-b')

        _ = edit_channel_by_name(page, base_url, Service_Typed, {
            'security': f'Basic Auth/{definition_a["name"]}',
        })

        _ = edit_channel_by_name(page, base_url, Service_Untyped, {
            'security': f'Basic Auth/{definition_b["name"]}',
        })

        # .. user A's document has only A's path and only A's schemas ..
        console_login(page, console_url, definition_a['username'], definition_a['password'])

        def has_only_typed_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Typed}
            return out

        spec = wait_for_spec(page, console_url, has_only_typed_path)

        schema_names = sorted(spec_schema_names(spec))
        assert schema_names == _Typed_Schema_Names, f'Unexpected schemas for user A: {schema_names}'

        # .. and B's path leaks nowhere into A's document, in JSON or in YAML.
        json_text = dumps(spec)
        yaml_text = page.request.get(console_url + Spec_YAML_Path).text()

        assert Path_Untyped not in json_text, f'User B\'s path leaked into user A\'s JSON document'
        assert Path_Untyped not in yaml_text, f'User B\'s path leaked into user A\'s YAML document'

        # Now the same the other way around - user B's document has only B's path
        # and no schemas at all, because the untyped endpoint references no models ..
        console_login(page, console_url, definition_b['username'], definition_b['password'])

        def has_only_untyped_path(spec:'anydict') -> 'bool':
            out = spec_paths(spec) == {Path_Untyped}
            return out

        spec = wait_for_spec(page, console_url, has_only_untyped_path)

        schema_names = sorted(spec_schema_names(spec))
        assert schema_names == [], f'Expected no schemas for user B, got: {schema_names}'

        # .. the YAML document is equivalent to the JSON one ..
        yaml_spec = get_spec_yaml(page, console_url)
        assert spec_paths(yaml_spec) == {Path_Untyped}, f'Unexpected YAML paths for user B: {spec_paths(yaml_spec)}'

        # .. and neither A's path nor A's schema names leak into B's documents.
        json_text = dumps(spec)
        yaml_text = page.request.get(console_url + Spec_YAML_Path).text()

        for leaked_name in [Path_Typed] + _Typed_Schema_Names:
            assert leaked_name not in json_text, f'`{leaked_name}` leaked into user B\'s JSON document'
            assert leaked_name not in yaml_text, f'`{leaked_name}` leaked into user B\'s YAML document'

# ################################################################################################################################
# ################################################################################################################################
