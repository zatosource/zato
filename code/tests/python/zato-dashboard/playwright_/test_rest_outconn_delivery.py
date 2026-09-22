# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Delivery tab of an outgoing REST connection.

# Zato
from zato.common.api import HTTP_SOAP, ZATO_NONE
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, create_topic, open_create_dialog, submit_create_form, \
     submit_edit_form

# Tests
from delivery_tab import accept_popover, click_switch, Field_Action, Field_Backoff_Multiplier, Field_Backoff_Threshold, \
     Field_Forward_To, Field_Keep_Header, Field_Max_Retries, Field_Retries, Field_Retry_Interval, Field_Sleep_Time, \
     Field_Use_DLQ, Field_Use_Queue, fill_popover, get_field_value, is_checked, Line_Action, Line_Retries, line_is_off, \
     open_popover, panel_is_off, popover_row_is_visible, set_popover_values, summary_text, switch_to_tab, Unit_Suffix
from rest_outconn import fill_outconn_form, get_outconn_id, open_edit_dialog, open_outconn_page, wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

_Test_Name_Prefix = 'test.rest.outconn.delivery.' + CryptoManager.generate_hex_string(32) + '.'

_Page_Prefix = 'http-soap'

# Never called by this test
_Host = 'http://127.0.0.1:1'

_Tab_Order = ['config', 'alerts', 'scheduler', 'delivery', 'request', 'response', 'callback']

_Service_Get = 'zato.http-soap.get'

_Default_Retries_Summary = 'No retries'
_Default_Action_Summary = 'Keep in DLQ'

# What the create dialog stores
_Created_Max_Retries = '3'
_Created_Sleep_Time = '2'
_Created_Sleep_Time_Unit = 'minute'
_Created_Multiplier = '3'
_Created_Threshold = '1'
_Created_Threshold_Unit = 'hour'
_Created_Retries_Summary = '3 retries, 2 minutes then 3x longer, 1 hour at most'

# The same waits in seconds
_Created_Sleep_Time_Seconds = 120
_Created_Threshold_Seconds = 3600

_Created_DLQ_Retries = '4'
_Created_DLQ_Interval = '5'
_Created_DLQ_Interval_Unit = 'minute'
_Created_DLQ_Interval_Seconds = 300
_Created_Action_Summary = '4 retries, every 5 minutes'

# What the edit dialog stores
_Edited_Action_Summary = 'Forward to {topic} without the DLQ header'

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'list[str]':
    """ The tabs of a dialog in the order they stand on the strip.
    """
    out = page.eval_on_selector_all(f'#{form_type}-div .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
    return out

# ################################################################################################################################

def _open_create_dialog(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Opens the create dialog on the outgoing REST page with the Config tab filled in.
    """
    open_outconn_page(page, base_url)
    open_create_dialog(page)

    fill_outconn_form(page, {
        'name': name,
        'host': _Host,
        'url_path': '/test/delivery/' + CryptoManager.generate_hex_string(8),
        'security_value': ZATO_NONE,
    })

# ################################################################################################################################

def _get_stored(api_client:'ZatoClient', name:'str') -> 'anydict':
    """ A connection as the server stores it.
    """
    out = api_client.invoke(_Service_Get, {'name': name})
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnDelivery:

    def test_create_dialog_delivery_tab(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The Delivery tab of the create dialog at its defaults.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_create_dialog(page, base_url, _Test_Name_Prefix + 'tab')

        assert _tab_names(page, 'create') == _Tab_Order, _tab_names(page, 'create')

        switch_to_tab(page, _Page_Prefix, 'create')

        assert summary_text(page, _Page_Prefix, 'create', Line_Retries) == _Default_Retries_Summary
        assert summary_text(page, _Page_Prefix, 'create', Line_Action) == _Default_Action_Summary
        assert not is_checked(page, 'create', Field_Use_Queue)
        assert is_checked(page, 'create', Field_Use_DLQ)

        assert get_field_value(page, 'create', Field_Max_Retries) == '0'
        assert get_field_value(page, 'create', Field_Action) == _dlq.Action.Keep
        assert get_field_value(page, 'create', Field_Retries) == '3'
        assert get_field_value(page, 'create', Field_Retry_Interval) == '1'
        assert get_field_value(page, 'create', Field_Retry_Interval + Unit_Suffix) == 'minute'

        assert panel_is_off(page, _Page_Prefix, 'create')
        click_switch(page, 'create', Field_Use_Queue)
        assert not panel_is_off(page, _Page_Prefix, 'create')

        assert not line_is_off(page, _Page_Prefix, 'create', Line_Action)
        click_switch(page, 'create', Field_Use_DLQ)
        assert line_is_off(page, _Page_Prefix, 'create', Line_Action)
        click_switch(page, 'create', Field_Use_DLQ)

        open_popover(page, _Page_Prefix, 'create', Line_Action)

        assert not popover_row_is_visible(page, Field_Retries)
        assert not popover_row_is_visible(page, Field_Forward_To)
        assert not popover_row_is_visible(page, Field_Keep_Header)

        fill_popover(page, {Field_Action: _dlq.Action.Retry})
        assert popover_row_is_visible(page, Field_Retries)
        assert popover_row_is_visible(page, Field_Retry_Interval)
        assert not popover_row_is_visible(page, Field_Forward_To)

        fill_popover(page, {Field_Action: _dlq.Action.Forward})
        assert not popover_row_is_visible(page, Field_Retries)
        assert popover_row_is_visible(page, Field_Forward_To)
        assert popover_row_is_visible(page, Field_Keep_Header)

        fill_popover(page, {Field_Action: _dlq.Action.Discard})
        assert not popover_row_is_visible(page, Field_Retries)
        assert not popover_row_is_visible(page, Field_Forward_To)
        assert not popover_row_is_visible(page, Field_Keep_Header)

        accept_popover(page)
        assert summary_text(page, _Page_Prefix, 'create', Line_Action) == 'Discard'

        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################

    def test_create_stores_the_delivery_settings(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
    ) -> 'None':
        """ What the popovers set is what the connection is created with.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Test_Name_Prefix + 'create'

        _open_create_dialog(page, base_url, name)
        switch_to_tab(page, _Page_Prefix, 'create')

        click_switch(page, 'create', Field_Use_Queue)

        set_popover_values(page, _Page_Prefix, 'create', Line_Retries, {
            Field_Max_Retries: _Created_Max_Retries,
            Field_Sleep_Time: _Created_Sleep_Time,
            Field_Sleep_Time + Unit_Suffix: _Created_Sleep_Time_Unit,
            Field_Backoff_Multiplier: _Created_Multiplier,
            Field_Backoff_Threshold: _Created_Threshold,
            Field_Backoff_Threshold + Unit_Suffix: _Created_Threshold_Unit,
        })
        assert summary_text(page, _Page_Prefix, 'create', Line_Retries) == _Created_Retries_Summary

        set_popover_values(page, _Page_Prefix, 'create', Line_Action, {
            Field_Action: _dlq.Action.Retry,
            Field_Retries: _Created_DLQ_Retries,
            Field_Retry_Interval: _Created_DLQ_Interval,
            Field_Retry_Interval + Unit_Suffix: _Created_DLQ_Interval_Unit,
        })
        assert summary_text(page, _Page_Prefix, 'create', Line_Action) == _Created_Action_Summary

        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)

        stored = _get_stored(api_client, name)

        assert stored['use_queue'] is True
        assert stored['max_retries'] == int(_Created_Max_Retries)
        assert stored['retry_sleep_time'] == _Created_Sleep_Time_Seconds
        assert stored['retry_backoff_multiplier'] == int(_Created_Multiplier)
        assert stored['retry_backoff_threshold'] == _Created_Threshold_Seconds

        assert stored['use_dlq'] is True
        assert stored['dlq_action'] == _dlq.Action.Retry
        assert stored['dlq_retries'] == int(_Created_DLQ_Retries)
        assert stored['dlq_retry_interval'] == _Created_DLQ_Interval_Seconds
        assert stored['dlq_forward_to'] == ''
        assert stored['dlq_keep_header'] is True

        open_edit_dialog(page, get_outconn_id(page, name))
        switch_to_tab(page, _Page_Prefix, 'edit')

        assert is_checked(page, 'edit', Field_Use_Queue)
        assert is_checked(page, 'edit', Field_Use_DLQ)
        assert not panel_is_off(page, _Page_Prefix, 'edit')

        assert get_field_value(page, 'edit', Field_Max_Retries) == _Created_Max_Retries
        assert get_field_value(page, 'edit', Field_Sleep_Time) == _Created_Sleep_Time
        assert get_field_value(page, 'edit', Field_Sleep_Time + Unit_Suffix) == _Created_Sleep_Time_Unit
        assert get_field_value(page, 'edit', Field_Backoff_Multiplier) == _Created_Multiplier
        assert get_field_value(page, 'edit', Field_Backoff_Threshold) == _Created_Threshold
        assert get_field_value(page, 'edit', Field_Backoff_Threshold + Unit_Suffix) == _Created_Threshold_Unit

        assert get_field_value(page, 'edit', Field_Action) == _dlq.Action.Retry
        assert get_field_value(page, 'edit', Field_Retries) == _Created_DLQ_Retries
        assert get_field_value(page, 'edit', Field_Retry_Interval) == _Created_DLQ_Interval
        assert get_field_value(page, 'edit', Field_Retry_Interval + Unit_Suffix) == _Created_DLQ_Interval_Unit

        assert summary_text(page, _Page_Prefix, 'edit', Line_Retries) == _Created_Retries_Summary
        assert summary_text(page, _Page_Prefix, 'edit', Line_Action) == _Created_Action_Summary

        page.click('#edit-div button:has-text("Cancel")')
        _ = page.wait_for_selector('#edit-div', state='hidden', timeout=5000)

# ################################################################################################################################

    def test_edit_stores_the_delivery_settings(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
    ) -> 'None':
        """ A connection created with the defaults reads them back in its edit dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Test_Name_Prefix + 'edit'

        # The topic has to exist before the page is loaded
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'topic')
        topic_name = topic['name']

        _open_create_dialog(page, base_url, name)
        submit_create_form(page)
        _ = wait_for_outconn_row(page, name)

        stored = _get_stored(api_client, name)
        assert stored['use_queue'] is False
        assert stored['use_dlq'] is True
        assert stored['dlq_action'] == _dlq.Action.Keep

        open_edit_dialog(page, get_outconn_id(page, name))
        switch_to_tab(page, _Page_Prefix, 'edit')

        assert not is_checked(page, 'edit', Field_Use_Queue)
        assert is_checked(page, 'edit', Field_Use_DLQ)
        assert panel_is_off(page, _Page_Prefix, 'edit')
        assert summary_text(page, _Page_Prefix, 'edit', Line_Retries) == _Default_Retries_Summary
        assert summary_text(page, _Page_Prefix, 'edit', Line_Action) == _Default_Action_Summary

        click_switch(page, 'edit', Field_Use_Queue)

        set_popover_values(page, _Page_Prefix, 'edit', Line_Retries, {
            Field_Max_Retries: _Created_Max_Retries,
            Field_Sleep_Time: _Created_Sleep_Time,
            Field_Sleep_Time + Unit_Suffix: _Created_Sleep_Time_Unit,
            Field_Backoff_Multiplier: _Created_Multiplier,
            Field_Backoff_Threshold: _Created_Threshold,
            Field_Backoff_Threshold + Unit_Suffix: _Created_Threshold_Unit,
        })

        set_popover_values(page, _Page_Prefix, 'edit', Line_Action, {
            Field_Action: _dlq.Action.Forward,
            Field_Forward_To: topic_name,
            Field_Keep_Header: False,
        })

        expected_action_summary = _Edited_Action_Summary.format(topic=topic_name)
        assert summary_text(page, _Page_Prefix, 'edit', Line_Action) == expected_action_summary

        submit_edit_form(page)

        stored = _get_stored(api_client, name)

        assert stored['use_queue'] is True
        assert stored['max_retries'] == int(_Created_Max_Retries)
        assert stored['retry_sleep_time'] == _Created_Sleep_Time_Seconds
        assert stored['retry_backoff_multiplier'] == int(_Created_Multiplier)
        assert stored['retry_backoff_threshold'] == _Created_Threshold_Seconds

        assert stored['use_dlq'] is True
        assert stored['dlq_action'] == _dlq.Action.Forward
        assert stored['dlq_forward_to'] == topic_name
        assert stored['dlq_keep_header'] is False

        open_edit_dialog(page, get_outconn_id(page, name))
        switch_to_tab(page, _Page_Prefix, 'edit')

        assert is_checked(page, 'edit', Field_Use_Queue)
        assert get_field_value(page, 'edit', Field_Action) == _dlq.Action.Forward
        assert get_field_value(page, 'edit', Field_Forward_To) == topic_name
        assert not is_checked(page, 'edit', Field_Keep_Header)
        assert summary_text(page, _Page_Prefix, 'edit', Line_Retries) == _Created_Retries_Summary
        assert summary_text(page, _Page_Prefix, 'edit', Line_Action) == expected_action_summary

        click_switch(page, 'edit', Field_Use_DLQ)
        assert line_is_off(page, _Page_Prefix, 'edit', Line_Action)

        submit_edit_form(page)

        stored = _get_stored(api_client, name)
        assert stored['use_dlq'] is False
        assert stored['dlq_action'] == _dlq.Action.Forward
        assert stored['dlq_forward_to'] == topic_name

# ################################################################################################################################
# ################################################################################################################################
