# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HL7 REST channel page with the C-CDA version - a channel created with it lists under that version, its edit form
# opens with the version preselected, switching the version to HL7 v2.x and back is an edit that sticks across a reload,
# and the channel deletes.

# pytest
import pytest

# Zato
from zato.common.api import HL7, ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog, set_select_value, submit_create_form, \
    submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url = '/zato/channel/hl7/rest/?cluster=1'

# The service every quickstart environment has
_Service = 'demo.ping'

_Name_Prefix = 'test.hl7.rest.ccda.' + CryptoManager.generate_hex_string(16)

_CCDA_Version = HL7.Const.Version.ccda.id
_V2_Version   = HL7.Const.Version.v2.id

# How long the list is given to show a saved row, in milliseconds
_Row_Timeout = 10000

# The version column of a row, counted the way the table's columns are declared
_Version_Cell_Index = 4

# ################################################################################################################################
# ################################################################################################################################

def _row(page:'Page', name:'str') -> 'any_':
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    out = page.wait_for_selector(row_selector, state='visible', timeout=_Row_Timeout)
    return out

# ################################################################################################################################

def _version_of(page:'Page', name:'str') -> 'str':
    row = _row(page, name)
    cells = row.query_selector_all('td')

    out = cells[_Version_Cell_Index].inner_text().strip()
    return out

# ################################################################################################################################

def _id_of(page:'Page', name:'str') -> 'str':
    row = _row(page, name)
    id_cell = row.query_selector('td[class*="item_id_"]')
    assert id_cell is not None, f'No id cell in the row of "{name}"'

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################

def _create(page:'Page', base_url:'str', name:'str', version:'str') -> 'str':
    """ Creates a channel through the page's own form and returns its id.
    """
    navigate_to_page(page, base_url, _Page_Url)
    open_create_dialog(page)

    page.fill('#id_name', name)
    page.fill('#id_url_path', '/' + name.replace('.', '/'))
    set_select_value(page, '#id_service', _Service)
    set_select_value(page, '#id_security_id', ZATO_NONE)
    set_select_value(page, '#id_hl7_version', version)

    submit_create_form(page)

    out = _id_of(page, name)
    return out

# ################################################################################################################################

def _open_edit(page:'Page', channel_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.channel.hl7.rest.edit("{channel_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=_Row_Timeout)

# ################################################################################################################################

def _delete(page:'Page', channel_id:'str') -> 'None':
    page.evaluate(f'$.fn.zato.channel.hl7.rest.delete_("{channel_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=_Row_Timeout)
    page.click('#popup_ok')
    _ = page.wait_for_selector(f'#tr_{channel_id}', state='detached', timeout=_Row_Timeout)

# ################################################################################################################################
# ################################################################################################################################

class TestHL7RESTChannelCCDA:

    # Deleting the channel removes its endpoint from the OpenAPI document, which the server notes as a breaking change
    @pytest.mark.expect_log_errors('OpenAPI breaking change:')
    def test_a_ccda_channel_lists_edits_and_deletes(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Name_Prefix + '.channel'

        # Created as a C-CDA channel, the new row says so ..
        channel_id = _create(page, base_url, name, _CCDA_Version)
        assert _version_of(page, name) == _CCDA_Version

        # .. and so does the row the server renders.
        navigate_to_page(page, base_url, _Page_Url)
        assert _version_of(page, name) == _CCDA_Version

        # The edit form opens with the version the channel has ..
        _open_edit(page, channel_id)
        assert page.input_value('#id_edit-hl7_version') == _CCDA_Version

        # .. switching it to HL7 v2.x is an edit ..
        set_select_value(page, '#id_edit-hl7_version', _V2_Version)
        submit_edit_form(page)
        assert _version_of(page, name) == _V2_Version

        navigate_to_page(page, base_url, _Page_Url)
        assert _version_of(page, name) == _V2_Version

        # .. and so is switching it back.
        _open_edit(page, channel_id)
        assert page.input_value('#id_edit-hl7_version') == _V2_Version

        set_select_value(page, '#id_edit-hl7_version', _CCDA_Version)
        submit_edit_form(page)

        navigate_to_page(page, base_url, _Page_Url)
        assert _version_of(page, name) == _CCDA_Version

        _delete(page, channel_id)

# ################################################################################################################################

    def test_both_versions_are_offered_and_v2_is_the_default(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        navigate_to_page(page, base_url, _Page_Url)
        open_create_dialog(page)

        options = page.eval_on_selector_all('#id_hl7_version option', 'items => items.map(item => item.value)')
        assert options == [_V2_Version, _CCDA_Version]

        labels = page.eval_on_selector_all('#id_hl7_version option', 'items => items.map(item => item.textContent)')
        assert labels == [HL7.Const.Version.v2.name, HL7.Const.Version.ccda.name]

        assert page.input_value('#id_hl7_version') == _V2_Version

# ################################################################################################################################
# ################################################################################################################################
