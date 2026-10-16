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
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_name_prefix = 'test.mcp.oauth.' + rand_string() + '.'

# The service every gateway in this suite exposes
_echo_service = 'demo.echo'

# The scope the gateway asks for
_scope = 'api://zato-mcp/tools.access'

# How long to wait for a UI change, in milliseconds
_ui_timeout = 10_000

# How far apart the bottom edges of the scopes box and its pane may be, in pixels
_bottom_edge_tolerance = 1

_security_body = '#mcp-wizard-security-body'
_scope_list = f'{_security_body} .mcp-scope-list'
_scope_text_field = f'{_scope_list} .search-field input'

# ################################################################################################################################
# ################################################################################################################################

def _open_tab(page:'Page', pane_name:'str') -> 'None':
    """ Opens the Security card and shows one of its two panes.
    """
    wizard_page.open_picker_card(page, 'security')

    page.click(f'#mcp-wizard-security-tabs .dashboard-tab[data-pane="{pane_name}"]')

    active_pane = f'{_security_body} .mcp-wizard-security-pane-active[data-pane="{pane_name}"]'
    _ = page.wait_for_selector(active_pane, state='attached', timeout=_ui_timeout)

# ################################################################################################################################

def _get_scope_chip_texts(page:'Page') -> 'strlist':
    """ What the scopes chips currently say, in order.
    """
    chips = page.query_selector_all(f'{_scope_list} li.search-choice span')

    out:'strlist' = []

    for chip in chips:
        text = chip.inner_text().strip()
        out.append(text)

    return out

# ################################################################################################################################

def _get_bottom_edge_distance(page:'Page') -> 'float':
    """ How far the bottom edge of the scopes box is from the bottom edge of its pane.
    """
    out = page.evaluate(f'''() => {{
        let pane = document.querySelector('{_security_body} .mcp-wizard-security-pane[data-pane="oauth"]');
        let box = document.querySelector('{_scope_list} .chosen-choices');
        return Math.abs(pane.getBoundingClientRect().bottom - box.getBoundingClientRect().bottom);
    }}''')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizardOAuth:
    """ The OAuth tab of the Security card - the scopes box is on screen and editable whether
    OAuth is on or off, fills its pane, and no scopes are stored while OAuth is off.
    """

    def test_create_and_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Types a scope with OAuth off on create, toggles OAuth, saves with OAuth off and reads it back.
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

        # .. the Security card opens on its definitions ..
        wizard_page.open_picker_card(page, 'security')

        is_picker_visible = page.is_visible('#badge-picker-sec-wizard')
        assert is_picker_visible, 'Expected the definitions pane on screen when the card opens'

        # .. the OAuth tab shows the scopes box with OAuth still off, editable and filling the pane ..
        _open_tab(page, 'oauth')

        is_oauth_on = page.is_checked(wizard_page.field_selector('oauth'))
        assert not is_oauth_on, 'Expected OAuth off on create'

        is_scope_field_visible = page.is_visible(_scope_text_field)
        is_scope_field_enabled = page.is_enabled(_scope_text_field)

        assert is_scope_field_visible, 'Expected the scopes box on screen while OAuth is off'
        assert is_scope_field_enabled, 'Expected the scopes box editable while OAuth is off'

        distance = _get_bottom_edge_distance(page)
        assert distance <= _bottom_edge_tolerance, f'Expected the scopes box to fill its pane, distance: {distance}'

        # .. a scope is typed in while OAuth is off ..
        page.fill(_scope_text_field, _scope)
        page.press(_scope_text_field, 'Enter')

        chips = _get_scope_chip_texts(page)
        assert chips == [_scope], f'Expected one scope chip, got: {chips}'

        # .. turning OAuth on and off again leaves the box and its chip as they were ..
        page.check(wizard_page.field_selector('oauth'))
        page.uncheck(wizard_page.field_selector('oauth'))

        is_scope_field_enabled = page.is_enabled(_scope_text_field)
        assert is_scope_field_enabled, 'Expected the scopes box editable after OAuth is turned off'

        chips = _get_scope_chip_texts(page)
        assert chips == [_scope], f'Expected the scope chip kept, got: {chips}'

        # .. and with OAuth off, the save stores OAuth off and no scopes.
        wizard_page.save_create(page)

        stored = masking_page.get_stored_gateway(zato_dashboard, gateway_name)

        assert not stored['oauth'], stored
        assert stored['oauth_scopes'] == '', stored

        # The edit wizard opens on OAuth off with an empty scopes box, still editable.
        wizard_page.open_wizard_edit(page, base_url, gateway_name)
        _open_tab(page, 'oauth')

        is_oauth_on = page.is_checked(wizard_page.field_selector('oauth', is_edit=True))
        assert not is_oauth_on, 'Expected OAuth off in the edit wizard'

        is_scope_field_enabled = page.is_enabled(_scope_text_field)
        assert is_scope_field_enabled, 'Expected the scopes box editable in the edit wizard'

        chips = _get_scope_chip_texts(page)
        assert chips == [], f'Expected no scope chips on edit, got: {chips}'

# ################################################################################################################################
# ################################################################################################################################
