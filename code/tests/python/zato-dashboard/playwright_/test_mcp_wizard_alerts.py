# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Zato
from zato.common.test import rand_string

# Zato - test helpers - the wizard driver lives next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_wizard as wizard_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mcp.wizard.alerts.' + rand_string() + '.'

# The service every gateway in this suite exposes
_Echo_Service = 'demo.echo'

# How long to wait for a UI element to show, in milliseconds
_UI_Timeout = 5000

# The Alerts popup the step 2 line opens, the popover one of its lines opens over it, and the button that accepts either
_Alerts_Popup = '#mcp-wizard-popup'
_Alerts_Line_Popover = '#alerts-tab-popup'
_Ok_Button = ' button.action-button'

# What the alerts test types - repeated calls over a shorter window and a volume in gigabytes over an hour
_Created_Repeat_Calls = '30'
_Created_Repeat_Calls_Window = '10'
_Created_Volume_Budget = '2'
_Created_Volume_Budget_Unit = 'gigabyte'
_Created_Volume_Budget_Window = '1'
_Created_Volume_Budget_Window_Unit = 'hour'

# The units the windows open with - what a count is read in until another unit is picked
_Default_Window_Unit = 'minute'

# ################################################################################################################################
# ################################################################################################################################

class TestMCPWizardAlerts:
    """ End-to-end test for the Alerts line of the MCP gateway wizard - the popup it opens, the popovers
    of its lines, what they write into the form, the review, the save and the edit reading it all back.
    """

# ################################################################################################################################

    def test_alerts(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The Alerts line of step 2 opens its popup, the repeated calls line inside it opens its own
        popover where the count and the window are typed, the response volume line takes a size with
        a unit of its own, what is typed reads back on the lines, in the hidden fields as seconds and
        bytes and in the review, the gateway is created with it and the edit wizard reads it back.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        gateway_name = _Test_Name_Prefix + 'alerts'
        url_path = '/mcp/wizard-alerts/' + rand_string()

        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        wizard_page.assign_badge(page, 'services', _Echo_Service)

        # The Alerts popup opens off its line on step 2 ..
        wizard_page.go_to_step(page, 1)

        page.click('#mcp-wizard-edit-alerts')
        _ = page.wait_for_selector(_Alerts_Popup, state='visible', timeout=_UI_Timeout)

        # .. with the volume line reading the default of a hundred megabytes ..
        volume_summary = page.inner_text('#mcp-wizard-alerts-summary-response_volume')
        assert '100 megabytes' in volume_summary, f'Expected the default volume on the line, got: "{volume_summary}"'

        # .. and the repeated calls line opens its own popover over the popup.
        page.click('#mcp-wizard-alerts-edit-repeated_calls')
        _ = page.wait_for_selector(_Alerts_Line_Popover, state='visible', timeout=_UI_Timeout)

        # The popover puts the cursor into its first input once its transition ends - typing
        # into another field before that would be pulled back into the first one
        repeat_input = '#alerts-tab-tippy-repeat_calls'
        _ = page.wait_for_function(
            f'document.activeElement && document.activeElement.id === "{repeat_input[1:]}"', timeout=_UI_Timeout)

        page.fill(repeat_input, _Created_Repeat_Calls)
        page.fill('#alerts-tab-tippy-repeat_calls_window', _Created_Repeat_Calls_Window)

        page.click(_Alerts_Line_Popover + _Ok_Button)
        _ = page.wait_for_selector(_Alerts_Line_Popover, state='hidden', timeout=_UI_Timeout)

        # The popover wrote into the form's hidden fields - the count, the window and its unit - and the line reads them back
        assert page.input_value('#id_alert_repeat_calls') == _Created_Repeat_Calls
        assert page.input_value('#id_alert_repeat_calls_window') == _Created_Repeat_Calls_Window
        assert page.input_value('#id_alert_repeat_calls_window_unit') == _Default_Window_Unit

        repeat_summary = page.inner_text('#mcp-wizard-alerts-summary-repeated_calls')
        assert _Created_Repeat_Calls in repeat_summary, f'Expected "{_Created_Repeat_Calls}" on the line, got: "{repeat_summary}"'
        assert '10 minutes' in repeat_summary, f'Expected the window on the line, got: "{repeat_summary}"'

        # The volume line takes a size with a unit of its own next to the window's
        page.click('#mcp-wizard-alerts-edit-response_volume')
        _ = page.wait_for_selector(_Alerts_Line_Popover, state='visible', timeout=_UI_Timeout)

        volume_input = '#alerts-tab-tippy-volume_budget'
        _ = page.wait_for_function(
            f'document.activeElement && document.activeElement.id === "{volume_input[1:]}"', timeout=_UI_Timeout)

        page.fill(volume_input, _Created_Volume_Budget)
        _ = page.select_option('#alerts-tab-tippy-volume_budget_unit', _Created_Volume_Budget_Unit)
        page.fill('#alerts-tab-tippy-volume_budget_window', _Created_Volume_Budget_Window)
        _ = page.select_option('#alerts-tab-tippy-volume_budget_window_unit', _Created_Volume_Budget_Window_Unit)

        page.click(_Alerts_Line_Popover + _Ok_Button)
        _ = page.wait_for_selector(_Alerts_Line_Popover, state='hidden', timeout=_UI_Timeout)

        # The hidden fields carry the size and the window with their units, the line reads gigabytes and an hour
        assert page.input_value('#id_alert_volume_budget') == _Created_Volume_Budget
        assert page.input_value('#id_alert_volume_budget_unit') == _Created_Volume_Budget_Unit
        assert page.input_value('#id_alert_volume_budget_window') == _Created_Volume_Budget_Window
        assert page.input_value('#id_alert_volume_budget_window_unit') == _Created_Volume_Budget_Window_Unit

        volume_summary = page.inner_text('#mcp-wizard-alerts-summary-response_volume')
        assert '2 gigabytes' in volume_summary, f'Expected the gigabytes on the line, got: "{volume_summary}"'
        assert '1 hour' in volume_summary, f'Expected the hour on the line, got: "{volume_summary}"'

        # The popup closes and the step 2 line says the alerts are on
        page.click(_Alerts_Popup + _Ok_Button)
        _ = page.wait_for_selector(_Alerts_Popup, state='hidden', timeout=_UI_Timeout)

        line_summary = page.inner_text('#mcp-wizard-summary-alerts')
        assert line_summary.startswith('On'), f'Expected the Alerts line to say On, got: "{line_summary}"'

        # The review carries the two lines ..
        wizard_page.go_to_step(page, wizard_page.Review_Step)

        review_text = page.inner_text('#mcp-wizard-review')
        assert '2 gigabytes' in review_text, f'Expected the volume in the review, got: "{review_text}"'
        assert _Created_Repeat_Calls in review_text, f'Expected the repeat count in the review, got: "{review_text}"'

        # .. and the gateway is created with them - stored as seconds and bytes, split back into the same
        # counts and units for the edit wizard.
        wizard_page.save_create(page)

        wizard_page.open_wizard_edit(page, base_url, gateway_name)

        assert page.input_value('#id_edit-alert_repeat_calls') == _Created_Repeat_Calls
        assert page.input_value('#id_edit-alert_repeat_calls_window') == _Created_Repeat_Calls_Window
        assert page.input_value('#id_edit-alert_repeat_calls_window_unit') == _Default_Window_Unit
        assert page.input_value('#id_edit-alert_volume_budget') == _Created_Volume_Budget
        assert page.input_value('#id_edit-alert_volume_budget_unit') == _Created_Volume_Budget_Unit
        assert page.input_value('#id_edit-alert_volume_budget_window') == _Created_Volume_Budget_Window
        assert page.input_value('#id_edit-alert_volume_budget_window_unit') == _Created_Volume_Budget_Window_Unit

        wizard_page.go_to_step(page, 1)

        page.click('#mcp-wizard-edit-alerts')
        _ = page.wait_for_selector(_Alerts_Popup, state='visible', timeout=_UI_Timeout)

        volume_summary = page.inner_text('#mcp-wizard-alerts-summary-response_volume')
        assert '2 gigabytes' in volume_summary, f'Expected the gigabytes on the line on edit, got: "{volume_summary}"'

        repeat_summary = page.inner_text('#mcp-wizard-alerts-summary-repeated_calls')
        assert '10 minutes' in repeat_summary, f'Expected the window on the line on edit, got: "{repeat_summary}"'

# ################################################################################################################################
# ################################################################################################################################

