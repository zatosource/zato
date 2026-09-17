# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing SOAP connection - the tab is on the page, a threshold and the status codes
# change through their popovers, the Active slider flips, and all of it comes back after a save.

# Zato
from zato.common.api import ZATO_NONE
from zato.common.crypto.api import CryptoManager

# Tests
from alerts_tab import click_active_slider, get_field_value, is_checked, set_chips_value, set_popover_value, summary_text, \
     switch_to_tab, Field_Consecutive_Failures, Field_Is_Active, Line_Failures_In_A_Row, Tab_Alerts, Tab_Main
from soap_outconn import create_soap_outconn, delete_soap_outconn, fill_soap_outconn_form, get_soap_outconn_id, \
     open_create_dialog, open_edit_dialog, open_soap_outconn_page, submit_create_form, wait_for_soap_outconn_row
from zato.common.test.playwright_pubsub import submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.soap.outconn.alerts.' + CryptoManager.generate_hex_string(32) + '.'

# The prefix the outgoing SOAP page names its tab panels after
_Page_Prefix = 'out-soap'

# The host the connection points at - never called by this test
_Host = 'https://soap.example.com'

# The status codes line and the fields behind it
_Line_Status_Codes = 'status_codes'
_Field_Status_Codes = 'status_codes'
_Field_Status_Code_Threshold = 'status_code_threshold'

# The values the round trip stores, well away from the seeded defaults of 3 and `401, 403, 5xx`
_Edited_Consecutive_Failures = '7'
_Edited_Status_Codes = '500, 503'
_Edited_Status_Code_Threshold = '2'

# The SOAP faults line and the fields behind it - the line an outgoing SOAP connection has and a REST one does not
_Line_SOAP_Faults = 'soap_faults'
_Field_Fault_Codes = 'fault_codes'
_Field_Fault_Threshold = 'fault_threshold'
_Default_Fault_Codes = 'Receiver, Server, Sender, Client'

# The values the create dialog stores, well away from the seeded defaults of `Receiver, Server, Sender, Client` and 3
_Created_Fault_Codes = 'Receiver, x:Timeout'
_Created_Fault_Threshold = '5'

# Where the tabs of the create dialog stand - Main first, Alerts right after it, before the SOAP tab
_Create_Tab_Order = ['main', 'alerts', 'soap']

# The lines of the tab in the order they are read - the faults right after the status codes
_Line_Order_Around_Faults = ['status_codes', 'soap_faults', 'connection_failures']

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'list[str]':
    """ The tabs of a dialog in the order they stand on the strip.
    """
    out = page.eval_on_selector_all(f'#{form_type}-div .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
    return out

# ################################################################################################################################

def _line_names(page:'Page', form_type:'str') -> 'list[str]':
    """ The popover lines of the Alerts tab in the order they are read.
    """
    selector = f'#{_Page_Prefix}-{form_type}-tab-panel-alerts a[id^="{_Page_Prefix}-{form_type}-tab-panel-alerts-edit-"]'
    prefix_len = len(f'{_Page_Prefix}-{form_type}-tab-panel-alerts-edit-')
    ids = page.eval_on_selector_all(selector, 'items => items.map(item => item.id)')

    out = []
    for item_id in ids:
        out.append(item_id[prefix_len:])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnAlerts:

    def test_create_dialog_alerts_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The Alerts tab of the create dialog is the second tab, has the SOAP faults line right after the status
        codes, and the fault codes and their threshold typed there are what the connection is created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        # The Alerts tab stands second, right after Main and before SOAP ..
        tab_names = _tab_names(page, 'create')
        assert tab_names[:3] == _Create_Tab_Order, tab_names

        # .. and it carries the faults line right after the status codes.
        switch_to_tab(page, _Page_Prefix, 'create', Tab_Alerts)

        line_names = _line_names(page, 'create')
        status_codes_idx = line_names.index('status_codes')
        assert line_names[status_codes_idx:status_codes_idx + 3] == _Line_Order_Around_Faults, line_names

        assert get_field_value(page, 'create', _Field_Fault_Codes) == _Default_Fault_Codes
        assert _Default_Fault_Codes in summary_text(page, _Page_Prefix, 'create', _Line_SOAP_Faults)

        # Type fault codes and a threshold of the connection's own through the line's popover ..
        set_chips_value(page, _Page_Prefix, 'create', _Line_SOAP_Faults, _Field_Fault_Codes, _Created_Fault_Codes)
        set_popover_value(page, _Page_Prefix, 'create', _Line_SOAP_Faults, _Field_Fault_Threshold, _Created_Fault_Threshold)

        faults_summary = summary_text(page, _Page_Prefix, 'create', _Line_SOAP_Faults)
        assert _Created_Fault_Codes in faults_summary
        assert _Created_Fault_Threshold in faults_summary

        # .. fill the connection's own fields on the Main tab and create ..
        name = _Test_Name_Prefix + 'create'
        fill_soap_outconn_form(page, {'name': name, 'host': _Host, 'security_value': ZATO_NONE})
        submit_create_form(page)

        _ = wait_for_soap_outconn_row(page, name)
        item_id = get_soap_outconn_id(page, name)

        # .. the edit form reads back what the create dialog stored ..
        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert get_field_value(page, 'edit', _Field_Fault_Codes) == _Created_Fault_Codes, \
            'The fault codes typed in the create dialog should come back on edit'
        assert get_field_value(page, 'edit', _Field_Fault_Threshold) == _Created_Fault_Threshold
        assert get_field_value(page, 'edit', _Field_Status_Codes) == '401, 403, 5xx'
        assert _Created_Fault_Codes in summary_text(page, _Page_Prefix, 'edit', _Line_SOAP_Faults)

        assert _tab_names(page, 'edit')[:3] == _Create_Tab_Order

        page.click('#edit-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#edit-div', state='hidden')

        # .. delete.
        open_soap_outconn_page(page, base_url)
        delete_soap_outconn(page, item_id)

# ################################################################################################################################

    def test_alerts_tab_round_trip(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Changes the failures threshold and the status codes through their popovers and flips the Active slider
        on the Alerts tab, saves, reopens the edit form and expects all of it to come back, with the Main tab
        still holding the connection's own fields.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection, which stores the seeded alert defaults ..
        name = _Test_Name_Prefix + 'round-trip'
        item_id = create_soap_outconn(page, base_url, name, _Host)

        # .. open the edit form and go to the Alerts tab ..
        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert is_checked(page, 'edit', Field_Is_Active), 'The Active slider should be on by default'
        assert get_field_value(page, 'edit', _Field_Status_Codes) == '401, 403, 5xx'

        # .. change the failures threshold through its popover, which rewrites the line's summary ..
        set_popover_value(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row, Field_Consecutive_Failures,
            _Edited_Consecutive_Failures)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures
        assert _Edited_Consecutive_Failures in summary_text(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row)

        # .. the status codes and how many responses it takes, through the popover of their line ..
        set_chips_value(page, _Page_Prefix, 'edit', _Line_Status_Codes, _Field_Status_Codes, _Edited_Status_Codes)
        set_popover_value(page, _Page_Prefix, 'edit', _Line_Status_Codes, _Field_Status_Code_Threshold,
            _Edited_Status_Code_Threshold)

        assert get_field_value(page, 'edit', _Field_Status_Codes) == _Edited_Status_Codes
        assert get_field_value(page, 'edit', _Field_Status_Code_Threshold) == _Edited_Status_Code_Threshold

        status_codes_summary = summary_text(page, _Page_Prefix, 'edit', _Line_Status_Codes)
        assert _Edited_Status_Codes in status_codes_summary
        assert _Edited_Status_Code_Threshold in status_codes_summary

        # .. flip the Active slider off and save ..
        click_active_slider(page, 'edit')
        assert not is_checked(page, 'edit', Field_Is_Active)

        submit_edit_form(page)

        # .. reopen the edit form - the Alerts tab reads what was saved ..
        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures, \
            'The edited threshold should come back after a save'
        assert get_field_value(page, 'edit', _Field_Status_Codes) == _Edited_Status_Codes, \
            'The edited status codes should come back after a save'
        assert get_field_value(page, 'edit', _Field_Status_Code_Threshold) == _Edited_Status_Code_Threshold
        assert not is_checked(page, 'edit', Field_Is_Active), 'The Active slider should stay off after a save'

        assert _Edited_Consecutive_Failures in summary_text(page, _Page_Prefix, 'edit', Line_Failures_In_A_Row)
        assert _Edited_Status_Codes in summary_text(page, _Page_Prefix, 'edit', _Line_Status_Codes)

        # .. and the Main tab still holds the connection's own fields ..
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Main)

        assert page.input_value('#id_edit-name') == name
        assert page.input_value('#id_edit-host') == _Host

        # .. save once more from the Main tab, which must not disturb the Alerts tab's values ..
        submit_edit_form(page)

        open_edit_dialog(page, item_id)
        switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

        assert get_field_value(page, 'edit', Field_Consecutive_Failures) == _Edited_Consecutive_Failures
        assert get_field_value(page, 'edit', _Field_Status_Codes) == _Edited_Status_Codes
        assert not is_checked(page, 'edit', Field_Is_Active)

        page.click('#edit-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#edit-div', state='hidden')

        # .. delete.
        open_soap_outconn_page(page, base_url)
        delete_soap_outconn(page, item_id)

# ################################################################################################################################
# ################################################################################################################################
