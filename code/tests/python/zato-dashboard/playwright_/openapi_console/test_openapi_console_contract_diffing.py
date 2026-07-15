# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# pytest
import pytest

from openapi_console_lib import console_login, edit_channel_by_name, read_fixture_services_source, \
    redeploy_fixture_services, snapshot_log_offsets, spec_paths, wait_for_log_line, wait_for_spec, \
    Admin_Username, Path_Diffing, Service_Diffing

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The lines the new version of the module no longer carries - one output field is gone
_Removed_Field_Line      = '    total_value:   int\n'
_Removed_Assignment_Line = '        out.total_value = 10_000\n'

# The exact warning the rebuild after the deployment must produce
_Expected_Change = 'OpenAPI breaking change: response field removed: total_value in POST ' + Path_Diffing

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleContractDiffing:
    """ Verifies that redeploying a service whose output lost a field makes the server
    report the breaking change against the previous document.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_contract_diffing(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Activates the diffing endpoint, hot-deploys a version with one output field removed
        and asserts the breaking-change warning in the server log.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        console_url = zato_dashboard['console_url']
        server_dir = zato_dashboard['server_dir']
        password = zato_dashboard['password']

        # Activate the diffing channel so its endpoint enters the document ..
        _ = edit_channel_by_name(page, base_url, Service_Diffing, {
            'is_active': True,
        })

        # .. sign in as admin and wait until the endpoint shows up, which confirms the servers
        # rebuilt their documents and now hold the pre-change contract to compare against ..
        console_login(page, console_url, Admin_Username, password)

        def has_diffing_path(spec:'anydict') -> 'bool':
            out = Path_Diffing in spec_paths(spec)
            return out

        _ = wait_for_spec(page, console_url, has_diffing_path)

        # .. build the new version of the module, with one output field removed ..
        source = read_fixture_services_source()

        assert _Removed_Field_Line in source, 'Expected the field line in the fixture source'
        assert _Removed_Assignment_Line in source, 'Expected the assignment line in the fixture source'

        source = source.replace(_Removed_Field_Line, '')
        source = source.replace(_Removed_Assignment_Line, '')

        # .. record the current log state and hot-deploy the new version ..
        logs_dir = os.path.join(server_dir, 'logs')
        offsets = snapshot_log_offsets(logs_dir)

        redeploy_fixture_services(server_dir, source)

        # .. and the rebuild after the deployment reports the removed field as a warning.
        line = wait_for_log_line(logs_dir, offsets, _Expected_Change)
        assert ' - WARNING - ' in line, f'Expected a WARNING line, got: {line}'

# ################################################################################################################################
# ################################################################################################################################
