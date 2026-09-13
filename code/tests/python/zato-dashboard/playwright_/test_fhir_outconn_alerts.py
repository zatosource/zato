# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing FHIR connection - the create dialog opens on Config with Alerts right after it, the tab
# carries the operation outcomes line right after the status codes, the outcome codes and their threshold typed there
# are what the connection is created with, and all of it comes back on edit.

# Zato
from zato.common.api import ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import set_select_value

# Tests
from alerts_tab import get_field_value, is_checked, set_chips_value, set_popover_value, summary_text, switch_to_tab, \
     Field_Is_Active, Tab_Alerts
from outgoing_fhir import delete_fhir_connection, get_fhir_conn_id, open_create_dialog, open_edit_dialog, open_fhir_page, \
     row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.fhir.outconn.alerts.' + CryptoManager.generate_hex_string(32) + '.'

# The prefix the outgoing FHIR page names its tab panels after
_Page_Prefix = 'out-fhir'

# The FHIR server the connection points at - nothing is ever sent to it
_Address = 'http://127.0.0.1:31999/fhir/r4'

# How long to wait for a dialog to close or a row to show up, in milliseconds
_Timeout = 10000

# The status codes line and the field behind it
_Field_Status_Codes = 'status_codes'
_Default_Status_Codes = '401, 403, 5xx'

# The operation outcomes line and the fields behind it - the line an outgoing FHIR connection has and a REST one does not
_Line_Operation_Outcomes = 'operation_outcomes'
_Field_Outcome_Codes = 'outcome_codes'
_Field_Outcome_Threshold = 'outcome_threshold'
_Default_Outcome_Codes = 'exception, transient, timeout, throttled, lock-error, no-store, too-costly'

# The values the create dialog stores, well away from the seeded defaults
_Created_Outcome_Codes = 'exception, not-found'
_Created_Outcome_Threshold = '5'

# Where the tabs of the dialogs stand - Config first, Alerts right after it
_Tab_Order = ['config', 'alerts']

# The lines of the tab in the order they are read - the outcomes right after the status codes
_Line_Order_Around_Outcomes = ['status_codes', 'operation_outcomes', 'connection_failures']

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'list[str]':
    """ The tabs of a dialog in the order they stand on the strip.
    """
    out = page.eval_on_selector_all(f'#{form_type}-div .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
    return out

# ################################################################################################################################

def _active_tab(page:'Page', form_type:'str') -> 'str':
    """ The tab a dialog is open on.
    """
    out = page.eval_on_selector(f'#{form_type}-div .dashboard-tab-active', 'item => item.dataset.tab')
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

class TestFHIROutconnAlerts:

    def test_create_dialog_alerts_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The create dialog opens on Config with Alerts second, the tab has the operation outcomes line right after
        the status codes, and the outcome codes and their threshold typed there are what the connection is created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_fhir_page(page, base_url)
        open_create_dialog(page)

        # The dialog opens on Config, with Alerts right after it ..
        assert _active_tab(page, 'create') == 'config'
        assert _tab_names(page, 'create') == _Tab_Order

        # .. and the Alerts tab carries the outcomes line right after the status codes.
        switch_to_tab(page, _Page_Prefix, 'create', Tab_Alerts)

        line_names = _line_names(page, 'create')
        status_codes_idx = line_names.index('status_codes')
        assert line_names[status_codes_idx:status_codes_idx + 3] == _Line_Order_Around_Outcomes, line_names
        assert 'soap_faults' not in line_names

        assert get_field_value(page, 'create', _Field_Outcome_Codes) == _Default_Outcome_Codes
        assert _Default_Outcome_Codes in summary_text(page, _Page_Prefix, 'create', _Line_Operation_Outcomes)
        assert is_checked(page, 'create', Field_Is_Active), 'The Active slider should be on by default'

        # Type outcome codes and a threshold of the connection's own through the line's popover ..
        set_chips_value(page, _Page_Prefix, 'create', _Line_Operation_Outcomes, _Field_Outcome_Codes, _Created_Outcome_Codes)
        set_popover_value(page, _Page_Prefix, 'create', _Line_Operation_Outcomes, _Field_Outcome_Threshold,
            _Created_Outcome_Threshold)

        outcomes_summary = summary_text(page, _Page_Prefix, 'create', _Line_Operation_Outcomes)
        assert _Created_Outcome_Codes in outcomes_summary
        assert _Created_Outcome_Threshold in outcomes_summary

        # .. fill the connection's own fields on the Config tab and create ..
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
            # .. the edit form opens on Config too and reads back what the create dialog stored ..
            open_edit_dialog(page, item_id)

            assert _active_tab(page, 'edit') == 'config'
            assert _tab_names(page, 'edit') == _Tab_Order

            switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

            assert get_field_value(page, 'edit', _Field_Outcome_Codes) == _Created_Outcome_Codes, \
                'The outcome codes typed in the create dialog should come back on edit'
            assert get_field_value(page, 'edit', _Field_Outcome_Threshold) == _Created_Outcome_Threshold
            assert get_field_value(page, 'edit', _Field_Status_Codes) == _Default_Status_Codes
            assert _Created_Outcome_Codes in summary_text(page, _Page_Prefix, 'edit', _Line_Operation_Outcomes)

            page.click('#edit-div button:has-text("Cancel")')
            _ = page.wait_for_selector('#edit-div', state='hidden')

        finally:
            # .. delete.
            open_fhir_page(page, base_url)
            delete_fhir_connection(page, item_id)

# ################################################################################################################################
# ################################################################################################################################
