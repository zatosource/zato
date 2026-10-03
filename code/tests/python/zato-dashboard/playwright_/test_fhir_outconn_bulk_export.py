# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Bulk export tab of an outgoing FHIR connection - the tab stands right after Config, the Group ID and Patient IDs
# rows follow the level picked, a destination added through the picker becomes a badge and lands in the hidden field,
# what was typed is what the connection is created with and all of it comes back on edit, and the row's Bulk exports
# link opens the page of the connection's jobs.

# stdlib
from json import loads

# Zato
from zato.common.api import ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import set_select_value

# Tests
from alerts_tab import switch_to_tab
from outgoing_fhir import delete_fhir_connection, get_fhir_conn_id, open_create_dialog, open_edit_dialog, open_fhir_page, \
     row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.fhir.outconn.bulk.' + CryptoManager.generate_hex_string(32) + '.'

# The prefix the outgoing FHIR page names its tab panels after
_Page_Prefix = 'out-fhir'

_Tab_Bulk_Export = 'bulk-export'

# The FHIR server the connection points at - nothing is ever sent to it
_Address = 'http://127.0.0.1:31999/fhir/r4'

# How long to wait for a dialog to close or a row to show up, in milliseconds
_Timeout = 10000

# What the tab is filled with
_Group_ID = 'diabetes-registry'
_Type_List = ['Patient', 'Observation']

# The resource types are chips and the field behind them joins what was typed
_Types = ', '.join(_Type_List)
_Since = '2026-01-01T00:00:00Z'
_Run_Every = '1'
_Run_Unit = 'days'

# The destination added through the picker - a service, there always being one to pick
_Destination_Type = 'service'
_Destination_Connection = 'demo.ping'

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'list[str]':
    out = page.eval_on_selector_all(f'#{form_type}-div .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
    return out

# ################################################################################################################################

def _field_prefix(form_type:'str') -> 'str':
    if form_type == 'edit':
        out = 'edit-'
    else:
        out = ''
    return out

# ################################################################################################################################

def _field(form_type:'str', name:'str') -> 'str':
    out = f'#id_{_field_prefix(form_type)}{name}'
    return out

# ################################################################################################################################

def _panel(form_type:'str') -> 'str':
    out = f'{_Page_Prefix}-{form_type}-tab-panel-{_Tab_Bulk_Export}'
    return out

# ################################################################################################################################

def _is_row_visible(page:'Page', form_type:'str', row_class:'str') -> 'bool':
    out = page.is_visible(f'#{_panel(form_type)} tr.{row_class}')
    return out

# ################################################################################################################################

def _fill_chip_list(page:'Page', form_type:'str', name:'str', values:'list[str]') -> 'None':
    """ Types each value into the chip list standing in for the field, Enter turning it into a chip.
    """
    text_field = f'{_field(form_type, name)} + .zato-chip-list input[type="text"]'

    for value in values:
        page.fill(text_field, value)
        page.press(text_field, 'Enter')

# ################################################################################################################################

def _badge_texts(page:'Page', form_type:'str') -> 'list[str]':
    selector = f'#{_panel(form_type)}-destination-badges .fhir-bulk-export-badge'
    out = page.eval_on_selector_all(selector, 'items => items.map(item => item.innerText.trim())')
    return out

# ################################################################################################################################

def _add_destination(page:'Page', form_type:'str') -> 'None':
    """ Picks the service destination in the picker and adds it.
    """
    type_select = _field(form_type, 'fhir-bulk-export-destination-type')
    connection_select = _field(form_type, 'fhir-bulk-export-destination-connection')

    _ = page.select_option(type_select, _Destination_Type)

    # The connections arrive from the server once per page, so the option may take a moment
    _ = page.wait_for_selector(f'{connection_select} option[value="{_Destination_Connection}"]', state='attached',
        timeout=_Timeout)
    _ = page.select_option(connection_select, _Destination_Connection)

    page.click(f'#{_panel(form_type)}-destination-add')

# ################################################################################################################################
# ################################################################################################################################

class TestFHIROutconnBulkExport:

    def test_create_dialog_bulk_export_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The tab follows the level picked, the picker turns a destination into a badge and the hidden field,
        the values typed are what the connection is created with and they come back on edit, and the row links
        to the page of the connection's exports.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_fhir_page(page, base_url)
        open_create_dialog(page)

        # The tab stands right after Config ..
        tab_names = _tab_names(page, 'create')
        assert tab_names[0] == 'config'
        assert tab_names[1] == _Tab_Bulk_Export

        switch_to_tab(page, _Page_Prefix, 'create', _Tab_Bulk_Export)

        # .. the export is off by default, at the group level with the Group ID row showing ..
        assert not page.is_checked(_field('create', 'bulk_export_is_active'))
        assert page.input_value(_field('create', 'bulk_export_level')) == 'group'
        assert _is_row_visible(page, 'create', 'fhir-bulk-export-row-group')
        assert not _is_row_visible(page, 'create', 'fhir-bulk-export-row-patient')

        # .. a patient-level export swaps the rows and a system-level one shows neither ..
        _ = page.select_option(_field('create', 'bulk_export_level'), 'patient')
        assert not _is_row_visible(page, 'create', 'fhir-bulk-export-row-group')
        assert _is_row_visible(page, 'create', 'fhir-bulk-export-row-patient')

        _ = page.select_option(_field('create', 'bulk_export_level'), 'system')
        assert not _is_row_visible(page, 'create', 'fhir-bulk-export-row-group')
        assert not _is_row_visible(page, 'create', 'fhir-bulk-export-row-patient')

        # .. back to a group export, filled in ..
        _ = page.select_option(_field('create', 'bulk_export_level'), 'group')
        page.set_checked(_field('create', 'bulk_export_is_active'), True)
        page.fill(_field('create', 'bulk_export_group_id'), _Group_ID)
        _fill_chip_list(page, 'create', 'bulk_export_types', _Type_List)
        page.fill(_field('create', 'bulk_export_since'), _Since)
        page.fill(_field('create', 'bulk_export_run_every'), _Run_Every)
        _ = page.select_option(_field('create', 'bulk_export_run_unit'), _Run_Unit)
        page.set_checked(_field('create', 'bulk_export_delete_on_server'), False)

        # .. a destination added through the picker is a badge and is in the hidden field ..
        assert _badge_texts(page, 'create') == []
        _add_destination(page, 'create')

        badges = _badge_texts(page, 'create')
        assert len(badges) == 1
        assert _Destination_Connection in badges[0]

        stored = loads(page.input_value(_field('create', 'bulk_export_destinations')))
        assert len(stored) == 1
        assert stored[0]['type'] == _Destination_Type
        assert stored[0]['connection'] == _Destination_Connection
        assert stored[0]['is_active'] is True

        # .. removing the badge empties the field and adding it again fills it ..
        page.click(f'#{_panel("create")}-destination-badges .fhir-bulk-export-badge-remove')
        assert _badge_texts(page, 'create') == []
        assert page.input_value(_field('create', 'bulk_export_destinations')) == ''

        _add_destination(page, 'create')
        assert len(_badge_texts(page, 'create')) == 1

        # .. the connection's own fields on the Config tab, and create.
        switch_to_tab(page, _Page_Prefix, 'create', 'config')

        name = _Test_Name_Prefix + 'create'
        page.fill('#id_name', name)
        page.fill('#id_address', _Address)
        set_select_value(page, '#id_security_id', ZATO_NONE)

        page.click('#create-div input[type="submit"]')
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Timeout)
        _ = page.wait_for_selector(row_selector(name), state='visible', timeout=_Timeout)

        item_id = get_fhir_conn_id(page, name)

        try:
            # The row links to the connection's exports ..
            row = page.query_selector(row_selector(name))
            assert row is not None
            link = row.query_selector('a:text-is("Bulk exports")')
            assert link is not None, 'Expected a Bulk exports link in the row'

            href = link.get_attribute('href')
            assert href == f'/zato/outgoing/hl7/fhir/bulk-export/{item_id}/cluster/1/', href

            # .. the edit form, opened from the server's copy of the row, reads back what was stored ..
            open_fhir_page(page, base_url)
            _ = page.wait_for_selector(row_selector(name), state='visible', timeout=_Timeout)
            open_edit_dialog(page, item_id)

            switch_to_tab(page, _Page_Prefix, 'edit', _Tab_Bulk_Export)

            assert page.is_checked(_field('edit', 'bulk_export_is_active'))
            assert page.input_value(_field('edit', 'bulk_export_level')) == 'group'
            assert page.input_value(_field('edit', 'bulk_export_group_id')) == _Group_ID
            assert page.input_value(_field('edit', 'bulk_export_types')) == _Types
            assert page.input_value(_field('edit', 'bulk_export_since')) == _Since
            assert page.input_value(_field('edit', 'bulk_export_run_every')) == _Run_Every
            assert page.input_value(_field('edit', 'bulk_export_run_unit')) == _Run_Unit
            assert page.is_checked(_field('edit', 'bulk_export_delete_files'))
            assert not page.is_checked(_field('edit', 'bulk_export_delete_on_server'))

            assert _is_row_visible(page, 'edit', 'fhir-bulk-export-row-group')

            badges = _badge_texts(page, 'edit')
            assert len(badges) == 1
            assert _Destination_Connection in badges[0]

            stored = loads(page.input_value(_field('edit', 'bulk_export_destinations')))
            assert stored[0]['connection'] == _Destination_Connection

            page.click('#edit-div button:has-text("Cancel")')
            _ = page.wait_for_selector('#edit-div', state='hidden')

            # .. and the exports page opens for the connection, with no job run yet.
            _ = page.goto(f'{base_url}{href}')
            _ = page.wait_for_selector('#fhir-bulk-export-conn-select', state='visible', timeout=_Timeout)

            assert page.input_value('#fhir-bulk-export-conn-select') == href
            assert page.input_value('#fhir-bulk-export-conn-name') == name
            assert page.is_visible('a:text-is("Run now")')

            rows = page.query_selector_all('#data-table tbody tr')
            assert len(rows) == 1, 'Expected the single row saying there are no jobs'

        finally:
            open_fhir_page(page, base_url)
            delete_fhir_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################
