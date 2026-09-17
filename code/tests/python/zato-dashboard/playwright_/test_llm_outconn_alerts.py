# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Alerts tab of an outgoing LLM connection - the create dialog opens on Config with Alerts right after it, the tab
# carries the truncated completions and the refusals under Failures and the token budget under Traffic, a budget of the
# connection's own in millions and a chip list of 429 alone typed there are what the connection is created with, and
# both come back on edit, the budget split back into its millions.

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

# Tests
from alerts_tab import get_field_value, is_checked, set_chips_value, set_popover_value_with_unit, summary_text, \
     switch_to_tab, Field_Is_Active, Tab_Alerts
from llm_outconn import delete_llm_outconn, fill_llm_outconn_form, get_llm_outconn_id, open_edit_dialog, \
     open_llm_outconn_page, wait_for_llm_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.llm.outconn.alerts.' + CryptoManager.generate_hex_string(32) + '.'

# The prefix the outgoing LLM page names its tab panels after
_Page_Prefix = 'out-llm'

# The provider the connection points at - nothing is ever sent to it
_Address = 'http://127.0.0.1:31999/v1'

# How long to wait for a dialog to close, in milliseconds
_Timeout = 10000

# The status codes line and the field behind it - the LLM's own default, with the 429 first
_Line_Status_Codes = 'status_codes'
_Field_Status_Codes = 'status_codes'
_Default_Status_Codes = '429, 401, 403, 5xx'

# The token budget line and the fields behind it - the count, its unit and the window
_Line_Token_Budget = 'token_budget'
_Field_Token_Budget = 'token_budget'
_Field_Token_Budget_Unit = 'token_budget_unit'
_Field_Token_Budget_Window = 'token_budget_window'
_Field_Token_Budget_Window_Unit = 'token_budget_window_unit'

# The seeded budget as the form shows it - ten millions over a day
_Default_Token_Budget = '10'
_Default_Token_Budget_Unit = 'million'
_Default_Token_Budget_Window = '1'
_Default_Token_Budget_Window_Unit = 'day'

# The values the create dialog stores, well away from the seeded defaults - the 429 alone and two and a half millions
_Created_Status_Codes = '429'
_Created_Token_Budget = '2.5'
_Created_Token_Budget_Unit = 'million'

# Where the tabs of the dialogs stand - Config first, Alerts right after it
_Tab_Order = ['config', 'alerts']

# The lines of the tab in the order they are read
_Line_Order = ['failures_in_a_row', 'error_rate', 'status_codes', 'connection_failures', 'truncated_completions', 'refusals',
    'slow_completions', 'token_budget']

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

class TestLLMOutconnAlerts:

    def test_create_dialog_alerts_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The create dialog opens on Config with Alerts second, the tab has the LLM's own lines among the others,
        and the budget in millions and the 429-only chip list typed there are what the connection is created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        open_llm_outconn_page(page, base_url)
        open_create_dialog(page)

        # The dialog opens on Config, with Alerts right after it ..
        assert _active_tab(page, 'create') == 'config'
        assert _tab_names(page, 'create') == _Tab_Order

        # .. and the Alerts tab carries the eight lines in their order, the LLM's own among them.
        switch_to_tab(page, _Page_Prefix, 'create', Tab_Alerts)

        assert _line_names(page, 'create') == _Line_Order

        assert get_field_value(page, 'create', _Field_Status_Codes) == _Default_Status_Codes
        assert _Default_Status_Codes in summary_text(page, _Page_Prefix, 'create', _Line_Status_Codes)
        assert is_checked(page, 'create', Field_Is_Active), 'The Active slider should be on by default'

        # The budget starts out as ten millions over a day ..
        assert get_field_value(page, 'create', _Field_Token_Budget) == _Default_Token_Budget
        assert get_field_value(page, 'create', _Field_Token_Budget_Unit) == _Default_Token_Budget_Unit
        assert get_field_value(page, 'create', _Field_Token_Budget_Window) == _Default_Token_Budget_Window
        assert get_field_value(page, 'create', _Field_Token_Budget_Window_Unit) == _Default_Token_Budget_Window_Unit

        budget_summary = summary_text(page, _Page_Prefix, 'create', _Line_Token_Budget)
        assert '10 millions tokens' in budget_summary
        assert '1 day' in budget_summary

        # .. a budget of the connection's own in millions and the 429 alone go through the popovers ..
        set_popover_value_with_unit(page, _Page_Prefix, 'create', _Line_Token_Budget, _Field_Token_Budget,
            _Created_Token_Budget, _Field_Token_Budget_Unit, _Created_Token_Budget_Unit)
        set_chips_value(page, _Page_Prefix, 'create', _Line_Status_Codes, _Field_Status_Codes, _Created_Status_Codes)

        assert '2.5 millions tokens' in summary_text(page, _Page_Prefix, 'create', _Line_Token_Budget)
        assert summary_text(page, _Page_Prefix, 'create', _Line_Status_Codes).count('429') == 1
        assert '401' not in summary_text(page, _Page_Prefix, 'create', _Line_Status_Codes)

        # .. fill the connection's own fields on the Config tab and create ..
        switch_to_tab(page, _Page_Prefix, 'create', 'config')

        name = _Test_Name_Prefix + 'create'
        fill_llm_outconn_form(page, {'name': name, 'address': _Address, 'model': 'gpt-4o-mini'})

        submit_create_form(page)
        _ = page.wait_for_selector('#create-div', state='hidden', timeout=_Timeout)
        _ = wait_for_llm_outconn_row(page, name)

        item_id = get_llm_outconn_id(page, name)

        try:
            # .. the edit form opens on Config too and reads back what the create dialog stored ..
            open_edit_dialog(page, item_id)

            assert _active_tab(page, 'edit') == 'config'
            assert _tab_names(page, 'edit') == _Tab_Order

            switch_to_tab(page, _Page_Prefix, 'edit', Tab_Alerts)

            assert get_field_value(page, 'edit', _Field_Status_Codes) == _Created_Status_Codes, \
                'The status codes typed in the create dialog should come back on edit'

            # The budget was stored as ones and comes back split into its millions
            assert get_field_value(page, 'edit', _Field_Token_Budget) == _Created_Token_Budget
            assert get_field_value(page, 'edit', _Field_Token_Budget_Unit) == _Created_Token_Budget_Unit
            assert get_field_value(page, 'edit', _Field_Token_Budget_Window) == _Default_Token_Budget_Window
            assert get_field_value(page, 'edit', _Field_Token_Budget_Window_Unit) == _Default_Token_Budget_Window_Unit

            assert '2.5 millions tokens' in summary_text(page, _Page_Prefix, 'edit', _Line_Token_Budget)
            assert '401' not in summary_text(page, _Page_Prefix, 'edit', _Line_Status_Codes)

            page.click('#edit-div button:has-text("Cancel")')
            _ = page.wait_for_selector('#edit-div', state='hidden')

        finally:
            # .. delete.
            open_llm_outconn_page(page, base_url)
            delete_llm_outconn(page, item_id)

# ################################################################################################################################
# ################################################################################################################################
