# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys

# Zato
from zato.common.test import rand_string

# Zato - test helpers - the wizard drivers live next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page
import _mcp_wizard_masking as masking_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.hooks.' + rand_string() + '.'

# The service every gateway in this suite exposes
_echo_service = 'demo.echo'

# The services the hooks invoke
_request_hook_service = 'demo.echo'
_response_hook_service = 'demo.ping'

# What a chip says when its hook has no service
_no_service = 'No service'

# ################################################################################################################################
# ################################################################################################################################

def _assert_stored(zato_dashboard:'anydict', gateway_name:'str', request_hook:'str', response_hook:'str') -> 'None':
    """ Reads the gateway back through the admin API and checks the two hook services it stores.
    """
    stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

    assert stored['request_hook_service'] == request_hook, stored
    assert stored['response_hook_service'] == response_hook, stored

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizardHooks:
    """ The hook services card of the MCP gateway wizard - the services picked on create are stored
    and restored on edit, and a hook removed on edit is stored without a service.
    """

    def test_create_and_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Picks a request and a response hook service on create, reads them back, then removes one on edit.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _test_name_prefix + 'round-trip'
        url_path = '/mcp/' + gateway_name

        # Step 1 - the gateway's name, path and one service ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill(wizard_page.field_selector('name'), gateway_name)
        page.fill(wizard_page.field_selector('url_path'), url_path)

        wizard_page.assign_badge(page, 'services', _echo_service)

        # .. step 2 - both hooks start without a service ..
        wizard_page.go_to_step(page, 1)
        wizard_page.open_hooks_card(page)

        for kind in (masking_page.Hook_Request, masking_page.Hook_Response):
            chip_text = masking_page.get_hook_chip_text(page, kind)
            assert chip_text == _no_service, chip_text

        # .. each is given one ..
        masking_page.pick_hook(page, masking_page.Hook_Request, _request_hook_service)
        masking_page.pick_hook(page, masking_page.Hook_Response, _response_hook_service)

        request_chip = masking_page.get_hook_chip_text(page, masking_page.Hook_Request)
        response_chip = masking_page.get_hook_chip_text(page, masking_page.Hook_Response)

        assert request_chip == _request_hook_service, request_chip
        assert response_chip == _response_hook_service, response_chip

        # .. and the save stores both.
        wizard_page.save_create(page)
        _assert_stored(zato_dashboard, gateway_name, _request_hook_service, _response_hook_service)

        # The edit wizard opens on the same services ..
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        wizard_page.go_to_step(page, 1)
        wizard_page.open_hooks_card(page)

        request_chip = masking_page.get_hook_chip_text(page, masking_page.Hook_Request)
        response_chip = masking_page.get_hook_chip_text(page, masking_page.Hook_Response)

        assert request_chip == _request_hook_service, request_chip
        assert response_chip == _response_hook_service, response_chip

        # .. and a hook removed there is stored without a service, the other one as it was.
        masking_page.remove_hook(page, masking_page.Hook_Request)

        request_chip = masking_page.get_hook_chip_text(page, masking_page.Hook_Request)
        assert request_chip == _no_service, request_chip

        wizard_page.save_edit(page)
        _assert_stored(zato_dashboard, gateway_name, '', _response_hook_service)

# ################################################################################################################################
# ################################################################################################################################
