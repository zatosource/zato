# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Bulk export tab of an outgoing FHIR connection - the tab stands right after Config, its popovers open while
# the export is off, the level picked on the tab line decides which popover its link opens, a destination assigned
# in the destinations popover lands in the line's summary and in the hidden field, what was entered is what the
# connection is created with and all of it comes back on edit, and the row's Bulk exports link opens the page of
# the connection's jobs.

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
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.fhir.outconn.bulk.' + CryptoManager.generate_hex_string(32) + '.'

# The prefix the outgoing FHIR page names its tab panels after
_Page_Prefix = 'out-fhir'

_Tab_Bulk_Export = 'bulk-export'

# Where the one open popover of the tab lives, and the prefix its inputs carry, from fhir-bulk-export-tab.js
_Popover_Selector = '#fhir-bulk-export-popup'
_Popover_Input_Prefix = 'fhir-bulk-export-tippy-'

# The button that writes a popover's answers back into the form
_Popover_Ok_Selector = _Popover_Selector + ' .micro-form-buttons button:text-is("OK")'

# The lines of the tab that open a popover
_Line_Level = 'level'
_Line_Resources = 'resources'
_Line_Schedule = 'schedule'
_Line_Destination = 'destination'

# The two zones of the destinations popover and a connection's badge in them, from fhir-bulk-export-destinations-zones.js
_Zone_Available = '#badge-zone-available-fhir-bulk-export'
_Zone_Assigned = '#badge-zone-assigned-fhir-bulk-export'
_Badge = ' .security-badge[data-type="{type}"][data-connection="{connection}"]'

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

# What the summary links read once the tab is filled in
_Summary_Level = _Group_ID
_Summary_Patients = '2 patients'
_Patient_List = ['p-1', 'p-2']
_Summary_Resources = _Types + ', since ' + _Since
_Summary_Schedule = 'Every 1 day'

# The destination added through the popover - a service, there always being one to pick
_Destination_Type = 'service'
_Destination_Connection = 'demo.ping'

# Whether the connections the destination popover offers have arrived from the server
_Connections_Loaded = '$.fn.zato.outgoing.hl7.fhir.bulk_export_tab.state.connectionData !== null'

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'strlist':
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

def _popover_input(name:'str') -> 'str':
    out = f'#{_Popover_Input_Prefix}{name}'
    return out

# ################################################################################################################################

def _summary_text(page:'Page', form_type:'str', line_name:'str') -> 'str':
    out = page.inner_text(f'#{_panel(form_type)}-summary-{line_name}')
    return out

# ################################################################################################################################

def _open_popover(page:'Page', form_type:'str', line_name:'str') -> 'None':
    page.click(f'#{_panel(form_type)}-edit-{line_name}')
    _ = page.wait_for_selector(_Popover_Selector, state='visible', timeout=_Timeout)

# ################################################################################################################################

def _accept_popover(page:'Page') -> 'None':
    page.click(_Popover_Ok_Selector)
    _ = page.wait_for_selector(_Popover_Selector, state='hidden', timeout=_Timeout)

# ################################################################################################################################

def _fill_chips(page:'Page', name:'str', values:'strlist') -> 'None':
    """ Types each value into the chips of an open popover, Enter turning it into a chip.
    """
    input_selector = _popover_input(name)

    for value in values:
        page.fill(input_selector, value)
        page.press(input_selector, 'Enter')

# ################################################################################################################################

def _badge(zone:'str', type_:'str', connection:'str') -> 'str':
    out = zone + _Badge.format(type=type_, connection=connection)
    return out

# ################################################################################################################################

def _is_assigned(page:'Page', type_:'str', connection:'str') -> 'bool':
    out = page.locator(_badge(_Zone_Assigned, type_, connection)).count() == 1
    return out

# ################################################################################################################################

def _toggle_destination(page:'Page', form_type:'str', is_assigned:'bool') -> 'None':
    """ Opens the destinations popover, moves the service's badge to the other zone and accepts the zones.
    """

    # The connections arrive from the server once per page ..
    _ = page.wait_for_function(_Connections_Loaded, timeout=_Timeout)

    # .. so the service has a badge in one of the zones ..
    _open_popover(page, form_type, _Line_Destination)
    _ = page.wait_for_selector(_badge(_Popover_Selector, _Destination_Type, _Destination_Connection), timeout=_Timeout)
    assert _is_assigned(page, _Destination_Type, _Destination_Connection) is (not is_assigned)

    # .. a click moves it to the other zone, a service carrying no options on its badge ..
    if is_assigned:
        page.click(_badge(_Zone_Available, _Destination_Type, _Destination_Connection))
    else:
        page.click(_badge(_Zone_Assigned, _Destination_Type, _Destination_Connection))

    assert _is_assigned(page, _Destination_Type, _Destination_Connection) is is_assigned
    assert page.locator(_badge(_Popover_Selector, _Destination_Type, _Destination_Connection) + ' a').count() == 0

    # .. and OK keeps the zones.
    _accept_popover(page)

# ################################################################################################################################
# ################################################################################################################################

class TestFHIROutconnBulkExport:

    def test_create_dialog_bulk_export_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The level link opens the popover of the level picked, the destinations popover fills the line's summary
        and the hidden field, the values entered are what the connection is created with and they come back on edit,
        and the row links to the page of the connection's exports.
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

        # .. the export is off by default, at the group level with no group picked yet and nowhere to deliver to ..
        assert not page.is_checked(_field('create', 'bulk_export_is_active'))
        assert page.input_value(_field('create', 'bulk_export_level')) == 'group'
        assert _summary_text(page, 'create', _Line_Level) == 'No group ID'
        assert _summary_text(page, 'create', _Line_Schedule) == 'Not scheduled'
        assert _summary_text(page, 'create', _Line_Destination) == 'None'

        level_select = _field('create', 'bulk_export_level')
        level_link = f'#{_panel("create")}-edit-{_Line_Level}'

        # .. a patient-level export links to the patient IDs alone, while the export is still off,
        # and its summary counts the patients rather than naming them ..
        _ = page.select_option(level_select, 'patient')
        assert _summary_text(page, 'create', _Line_Level) == 'No patient IDs'

        _open_popover(page, 'create', _Line_Level)
        assert page.is_visible(_popover_input('bulk_export_patient_ids'))
        assert page.locator(_popover_input('bulk_export_group_id')).count() == 0
        _fill_chips(page, 'bulk_export_patient_ids', _Patient_List)
        _accept_popover(page)
        assert _summary_text(page, 'create', _Line_Level) == _Summary_Patients

        # .. a system-level export takes nothing, so there is no link at all ..
        _ = page.select_option(level_select, 'system')
        assert not page.is_visible(level_link)

        # .. a group export links to the group ID alone, which is filled in ..
        _ = page.select_option(level_select, 'group')
        _open_popover(page, 'create', _Line_Level)
        assert page.locator(_popover_input('bulk_export_patient_ids')).count() == 0
        page.fill(_popover_input('bulk_export_group_id'), _Group_ID)
        _accept_popover(page)

        # .. the resources ..
        _open_popover(page, 'create', _Line_Resources)
        _fill_chips(page, 'bulk_export_types', _Type_List)
        page.fill(_popover_input('bulk_export_since'), _Since)
        _accept_popover(page)

        # .. the schedule ..
        _open_popover(page, 'create', _Line_Schedule)
        page.fill(_popover_input('bulk_export_run_every'), _Run_Every)
        _ = page.select_option(_popover_input('bulk_export_run_unit'), _Run_Unit)
        _accept_popover(page)

        page.set_checked(_field('create', 'bulk_export_delete_on_server'), False)

        # .. each line sums up what its popover holds ..
        assert _summary_text(page, 'create', _Line_Level) == _Summary_Level
        assert _summary_text(page, 'create', _Line_Resources) == _Summary_Resources
        assert _summary_text(page, 'create', _Line_Schedule) == _Summary_Schedule

        # .. a destination assigned in the popover is in the line's summary and in the hidden field ..
        _toggle_destination(page, 'create', True)
        assert _summary_text(page, 'create', _Line_Destination) == '1x Service'

        stored = loads(page.input_value(_field('create', 'bulk_export_destinations')))
        assert len(stored) == 1
        assert stored[0]['type'] == _Destination_Type
        assert stored[0]['connection'] == _Destination_Connection
        assert stored[0]['is_active'] is True

        # .. moving it back empties the field and assigning it again fills it ..
        _toggle_destination(page, 'create', False)
        assert _summary_text(page, 'create', _Line_Destination) == 'None'
        assert page.input_value(_field('create', 'bulk_export_destinations')) == ''

        _toggle_destination(page, 'create', True)
        assert len(loads(page.input_value(_field('create', 'bulk_export_destinations')))) == 1

        # .. the export is turned on ..
        page.set_checked(_field('create', 'bulk_export_is_active'), True)

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

            assert _summary_text(page, 'edit', _Line_Level) == _Summary_Level
            assert _summary_text(page, 'edit', _Line_Resources) == _Summary_Resources
            assert _summary_text(page, 'edit', _Line_Schedule) == _Summary_Schedule

            assert _summary_text(page, 'edit', _Line_Destination) == '1x Service'

            # .. the destinations popover has the connection assigned ..
            _open_popover(page, 'edit', _Line_Destination)
            _ = page.wait_for_selector(_badge(_Zone_Assigned, _Destination_Type, _Destination_Connection), timeout=_Timeout)
            assert _is_assigned(page, _Destination_Type, _Destination_Connection)
            page.click(f'{_Popover_Selector} .micro-form-buttons button:text-is("Cancel")')
            _ = page.wait_for_selector(_Popover_Selector, state='hidden', timeout=_Timeout)

            # .. as does the hidden field ..
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
