# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# pytest
import pytest

from openapi_console_lib import read_fixture_services_source, redeploy_fixture_services, snapshot_log_offsets, \
    wait_for_channel_row_reloading, wait_for_log_line, Fixture_Services_File_Name, Path_Prestarted, Service_Prestarted
from rest_channel import create_channel, delete_channel, get_channel_id, get_row_cell_texts, open_channel_page, \
    wait_for_channel_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Row cell indexes for REST channel rows
_Cell_Is_Active = 3
_Cell_Url_Path  = 4

# The URL path of the hand-made channel that takes precedence over auto-creation
_Handmade_Url_Path = '/test/openapi/handmade/ping'

# The line the server logs once a hot-deployed module has been processed
_Deployed_Line_Fragment = Fixture_Services_File_Name + '` ->'

# How long to wait for the deployment's configuration events to propagate
_Settle_Time = 3

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleRecreateAfterDelete:
    """ Verifies that a deleted auto-created channel comes back on the next deployment
    of its service and that a hand-made channel of the same name takes precedence.
    """

# ################################################################################################################################

    # Removing a documented endpoint is a breaking change the servers report on rebuild
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_recreate_after_delete(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Deletes the prestarted channel, redeploys its service and asserts the recreation,
        then repeats the cycle with a hand-made channel in place.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        source = read_fixture_services_source()

        # Delete the auto-created channel ..
        open_channel_page(page, base_url, query=Service_Prestarted)
        _ = wait_for_channel_row(page, Service_Prestarted)

        channel_id = get_channel_id(page, Service_Prestarted)
        delete_channel(page, channel_id)

        # .. redeploy the service through the pickup directory ..
        redeploy_fixture_services(server_dir, source)

        # .. the deployment finds the channel missing and recreates it ..
        row = wait_for_channel_row_reloading(page, base_url, Service_Prestarted)
        cells = get_row_cell_texts(row)

        # .. under the same convention-driven URL path ..
        assert cells[_Cell_Url_Path] == Path_Prestarted, f'Unexpected url_path after recreation: {cells}'

        # .. and active again, because the active pattern still matches the service.
        assert cells[_Cell_Is_Active] == 'Yes', f'Expected an active channel after recreation: {cells}'

        # Now delete the channel again ..
        channel_id = get_channel_id(page, Service_Prestarted)
        delete_channel(page, channel_id)

        # .. and hand-make a channel of the same name under a custom URL path.
        _ = create_channel(page, base_url, Service_Prestarted, Service_Prestarted, _Handmade_Url_Path)

        # Redeploy once more, waiting until the server reports the deployment in its log ..
        logs_dir = os.path.join(server_dir, 'logs')
        offsets = snapshot_log_offsets(logs_dir)

        redeploy_fixture_services(server_dir, source)
        _ = wait_for_log_line(logs_dir, offsets, _Deployed_Line_Fragment)

        # .. give the deployment's configuration events a moment to propagate ..
        time.sleep(_Settle_Time)

        # .. and the hand-made channel took precedence - its name already exists,
        # so the deployment created no auto channel and the custom URL path stays.
        open_channel_page(page, base_url, query=Service_Prestarted)
        row = wait_for_channel_row(page, Service_Prestarted)
        cells = get_row_cell_texts(row)

        assert cells[_Cell_Url_Path] == _Handmade_Url_Path, f'Expected the hand-made channel to remain: {cells}'

# ################################################################################################################################
# ################################################################################################################################
