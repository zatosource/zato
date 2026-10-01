# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io
Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The tabs of the Kafka dialogs - the Producer and Delivery tabs of an outgoing connection, the Consumer, Routing
# and Delivery tabs of a channel, the topics textarea, the routing editor and the DLQ page a channel's list links to.

# stdlib
import json

# Zato
from zato.common.api import HTTP_SOAP, KAFKA
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog, submit_create_form, \
     submit_edit_form

# Tests
from delivery_tab import click_switch, Field_Action, Field_Max_Retries, Field_Sleep_Time, Field_Use_DLQ, Field_Use_Queue, \
     get_field_value, is_checked, Line_Action, Line_Retries, panel_id, panel_is_off, set_popover_values, summary_text, \
     switch_to_tab, Unit_Suffix
from kafka_channel import create_kafka_channel, delete_kafka_channel, fill_kafka_channel_form, find_kafka_channel_row, \
     get_kafka_channel_id, open_edit_dialog as open_channel_edit_dialog, open_kafka_channel_page, wait_for_kafka_channel_row
from kafka_outconn import delete_kafka_outconn, fill_kafka_outconn_form, get_kafka_outconn_id, \
     open_edit_dialog as open_outconn_edit_dialog, open_kafka_outconn_page, wait_for_kafka_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist, strlist
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ
_producer = KAFKA.Producer
_consumer = KAFKA.Consumer
_routing = KAFKA.Routing

_Test_Name_Prefix = 'test.kafka.dashboard.tabs.' + CryptoManager.generate_hex_string(32) + '.'

# Never connected to by these tests
_Address = '127.0.0.1:1'

_Outconn_Page_Prefix = 'out-kafka'
_Channel_Page_Prefix = 'channel-kafka'

_Outconn_Type = 'outconn-kafka'
_Channel_Type = 'channel-kafka'

# The URL of a channel's DLQ page as its list links to it
_Channel_DLQ_Conn_Type = 'kafka-channel'
_Channel_DLQ_URL = '/zato/channel/delivery/{conn_type}/{conn_id}/?cluster=1&tab=dlq'

_Outconn_Tab_Order = ['config', 'producer', 'delivery']
_Channel_Tab_Order = ['config', 'consumer', 'routing', 'delivery']

_Service_Get_List = 'zato.generic.connection.get-list'

# Services every server has
_Channel_Service = 'zato.ping'
_Routing_Service = 'zato.helpers.input-logger'

# The popovers of each tab, from the JS of each tab and micro-forms/core.js
_Producer_Popover_Prefix = 'kafka-producer-tab'
_Consumer_Popover_Prefix = 'kafka-consumer-tab'
_Routing_Popover_Prefix = 'kafka-routing-tab'

_Popover_Timeout = 5000

# The lines of the Producer tab
_Line_Batches = 'batches'
_Line_Acks = 'acks'

# The lines of the Consumer tab
_Line_Limits = 'limits'
_Line_Dedup = 'dedup'

# What the Producer tab is changed to - each differs from its default
_Changed_Compression = 'gzip'
_Changed_Linger = '2'
_Changed_Linger_Unit = 'second'
_Changed_Linger_Ms = 2000
_Changed_Max_Message_Size = '3'
_Changed_Max_Message_Size_Unit = 'kilobyte'
_Changed_Max_Message_Size_Bytes = 3000
_Changed_Acks = '1'
_Changed_Send_Timeout = '2'
_Changed_Send_Timeout_Unit = 'minute'
_Changed_Send_Timeout_Seconds = 120

# What the Consumer tab is changed to
_Changed_Auto_Offset_Reset = 'earliest'
_Changed_Max_In_Flight = '7'
_Changed_Dedup_Header = 'X-Dedup-Id'
_Changed_Dedup_TTL = '3'
_Changed_Dedup_TTL_Unit = 'hour'
_Changed_Dedup_TTL_Seconds = 10800

# What the Delivery tab is changed to
_Changed_Max_Retries = '4'
_Changed_Sleep_Time = '3'
_Changed_Sleep_Time_Unit = 'minute'
_Changed_Sleep_Time_Seconds = 180

# The topics a channel is created with, one per line, and the comma-separated form the edit uses
_Topics_Lines = ['orders', 'invoices', 'shipments']
_Topics_Edited = ['returns', 'refunds']

# ################################################################################################################################
# ################################################################################################################################

def _tab_names(page:'Page', form_type:'str') -> 'strlist':
    """ The tabs of a dialog in the order they stand on the strip.
    """
    out = page.eval_on_selector_all(f'#{form_type}-div .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
    return out

# ################################################################################################################################

def _switch_to_tab(page:'Page', page_prefix:'str', form_type:'str', tab_name:'str') -> 'None':
    """ Clicks one tab of a dialog and waits for its panel to show.
    """
    page.click(f'#{form_type}-div .dashboard-tab[data-tab="{tab_name}"]')
    _ = page.wait_for_selector(f'#{page_prefix}-{form_type}-tab-panel-{tab_name}', state='visible', timeout=_Popover_Timeout)

# ################################################################################################################################

def _tab_panel_id(page_prefix:'str', form_type:'str', tab_name:'str') -> 'str':
    """ The id of one tab's panel in a dialog.
    """
    out = f'{page_prefix}-{form_type}-tab-panel-{tab_name}'
    return out

# ################################################################################################################################

def _field_id(form_type:'str', field_name:'str') -> 'str':
    """ The id of one field of a Django form, the edit form's fields carrying a prefix.
    """
    prefix = 'edit-' if form_type == 'edit' else ''
    out = f'id_{prefix}{field_name}'
    return out

# ################################################################################################################################

def _field_value(page:'Page', form_type:'str', field_name:'str') -> 'str':
    """ What one field of a dialog currently holds.
    """
    out = page.input_value(f'#{_field_id(form_type, field_name)}')
    return out

# ################################################################################################################################

def _open_tab_popover(page:'Page', page_prefix:'str', form_type:'str', tab_name:'str', line_name:'str', popover_prefix:'str') -> 'None':
    """ Opens the popover of one line of a tab through the line's summary link.
    """
    page.click(f'#{_tab_panel_id(page_prefix, form_type, tab_name)}-edit-{line_name}')
    _ = page.wait_for_selector(f'#{popover_prefix}-popup', state='visible', timeout=_Popover_Timeout)

# ################################################################################################################################

def _fill_tab_popover(page:'Page', popover_prefix:'str', values:'anydict') -> 'None':
    """ Sets the inputs of the open popover of a tab, by field name and in the order given.
    """
    for field_name, value in values.items():
        selector = f'#{popover_prefix}-tippy-{field_name}'
        tag_name = page.eval_on_selector(selector, 'item => item.tagName')
        if tag_name == 'SELECT':
            _ = page.select_option(selector, value)
        else:
            page.fill(selector, value)

# ################################################################################################################################

def _accept_tab_popover(page:'Page', popover_prefix:'str') -> 'None':
    """ Accepts the open popover of a tab.
    """
    page.click(f'#{popover_prefix}-popup .micro-form-buttons button:has-text("OK")')
    _ = page.wait_for_selector(f'#{popover_prefix}-popup', state='hidden', timeout=_Popover_Timeout)

# ################################################################################################################################

def _set_tab_popover_values(
    page:'Page',
    page_prefix:'str',
    form_type:'str',
    tab_name:'str',
    line_name:'str',
    popover_prefix:'str',
    values:'anydict',
) -> 'None':
    """ Opens the popover of a line of a tab, fills it in and accepts it.
    """
    _open_tab_popover(page, page_prefix, form_type, tab_name, line_name, popover_prefix)
    _fill_tab_popover(page, popover_prefix, values)
    _accept_tab_popover(page, popover_prefix)

# ################################################################################################################################

def _tab_summary(page:'Page', page_prefix:'str', form_type:'str', tab_name:'str', line_name:'str') -> 'str':
    """ What a line's summary link of a tab currently reads.
    """
    out = page.inner_text(f'#{_tab_panel_id(page_prefix, form_type, tab_name)}-summary-{line_name}')
    return out

# ################################################################################################################################

def _set_select(page:'Page', form_type:'str', field_name:'str', value:'str') -> 'None':
    """ Picks a value of a select that stands on a line of a tab, then tells the tab about it.
    """
    _ = page.select_option(f'#{_field_id(form_type, field_name)}', value)

# ################################################################################################################################

def _get_stored(api_client:'ZatoClient', type_:'str', name:'str') -> 'anydict':
    """ A generic connection as the server stores it.
    """
    items = api_client.invoke(_Service_Get_List, {'cluster_id': 1, 'type_': type_})

    for item in items:
        if item['name'] == name:
            out = item
            return out

    raise ValueError(f'Connection `{name}` of type `{type_}` not found in {items}')

# ################################################################################################################################

def _routing_rules(page:'Page', form_type:'str') -> 'anylist':
    """ The routing rules the hidden field of a channel dialog currently holds.
    """
    out = json.loads(_field_value(page, form_type, _consumer.Field_Routing))
    return out

# ################################################################################################################################

def _routing_rule_count(page:'Page', form_type:'str') -> 'int':
    """ How many rule lines the Routing tab shows.
    """
    out = page.locator(f'#{_tab_panel_id(_Channel_Page_Prefix, form_type, "routing")}-rules .kafka-routing-tab-rule').count()
    return out

# ################################################################################################################################

def _add_routing_rule(page:'Page', form_type:'str', topic:'str', header_name:'str', header_value:'str', service:'str') -> 'None':
    """ Adds one rule through the Routing tab's editor.
    """
    page.click(f'#{_tab_panel_id(_Channel_Page_Prefix, form_type, "routing")}-add')
    _ = page.wait_for_selector(f'#{_Routing_Popover_Prefix}-popup', state='visible', timeout=_Popover_Timeout)

    _fill_tab_popover(page, _Routing_Popover_Prefix, {
        'routing_topic': topic,
        'routing_header_name': header_name,
        'routing_header_value': header_value,
        'routing_service': service,
    })
    _accept_tab_popover(page, _Routing_Popover_Prefix)

# ################################################################################################################################

def _open_outconn_create_dialog(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Opens the create dialog of the outgoing Kafka page with its Config tab filled in.
    """
    open_kafka_outconn_page(page, base_url)
    open_create_dialog(page)
    fill_kafka_outconn_form(page, {
        'name': name,
        'address': _Address,
        'topic': name,
    })

# ################################################################################################################################

def _open_channel_create_dialog(page:'Page', base_url:'str', name:'str', topics:'str') -> 'None':
    """ Opens the create dialog of the Kafka channels page with its Config tab filled in.
    """
    open_kafka_channel_page(page, base_url)
    open_create_dialog(page)
    fill_kafka_channel_form(page, {
        'name': name,
        'address': _Address,
        'topics': topics,
        'group_id': name,
        'service': _Channel_Service,
    })

# ################################################################################################################################

def _cancel_edit_dialog(page:'Page') -> 'None':
    """ Closes an edit dialog without saving.
    """
    page.click('#edit-div button:has-text("Cancel")')
    _ = page.wait_for_selector('#edit-div', state='hidden', timeout=_Popover_Timeout)

# ################################################################################################################################
# ################################################################################################################################

class TestKafkaOutconnTabs:

    def test_create_dialog_has_the_producer_and_delivery_tabs_at_their_defaults(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
    ) -> 'None':
        """ The outgoing dialog has the Config, Producer and Delivery tabs, the Producer tab reads its defaults
        and the Delivery tab has the queue switch.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_outconn_create_dialog(page, base_url, _Test_Name_Prefix + 'outconn.tabs')
        assert _tab_names(page, 'create') == _Outconn_Tab_Order, _tab_names(page, 'create')

        _switch_to_tab(page, _Outconn_Page_Prefix, 'create', 'producer')

        assert _field_value(page, 'create', _producer.Field_Compression) == _producer.Default_Compression
        assert _field_value(page, 'create', _producer.Field_Acks) == _producer.Default_Acks
        assert _field_value(page, 'create', _producer.Field_Linger_Ms) == str(_producer.Default_Linger_Ms)
        assert _field_value(page, 'create', _producer.Field_Send_Timeout) == str(_producer.Default_Send_Timeout)
        assert page.is_checked(f'#{_field_id("create", _producer.Field_Is_Idempotent)}')

        assert 'All Kafka instances' in _tab_summary(page, _Outconn_Page_Prefix, 'create', 'producer', _Line_Acks)
        assert 'Each sent at once' in _tab_summary(page, _Outconn_Page_Prefix, 'create', 'producer', _Line_Batches)

        switch_to_tab(page, _Outconn_Page_Prefix, 'create')

        assert page.is_visible(f'#{panel_id(_Outconn_Page_Prefix, "create")}-line-use_queue')
        assert not is_checked(page, 'create', Field_Use_Queue)
        assert is_checked(page, 'create', Field_Use_DLQ)
        assert panel_is_off(page, _Outconn_Page_Prefix, 'create')

        click_switch(page, 'create', Field_Use_Queue)
        assert not panel_is_off(page, _Outconn_Page_Prefix, 'create')

        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################

    def test_create_and_edit_store_the_producer_and_delivery_settings(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
    ) -> 'None':
        """ What the Producer and Delivery tabs are set to is what the connection is stored with, the edit dialog
        reads it back and an edit stores the changes.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Test_Name_Prefix + 'outconn.store'

        _open_outconn_create_dialog(page, base_url, name)
        _switch_to_tab(page, _Outconn_Page_Prefix, 'create', 'producer')

        _set_select(page, 'create', _producer.Field_Compression, _Changed_Compression)

        _set_tab_popover_values(page, _Outconn_Page_Prefix, 'create', 'producer', _Line_Batches, _Producer_Popover_Prefix, {
            _producer.Field_Linger_Ms: _Changed_Linger,
            _producer.Field_Linger_Ms + Unit_Suffix: _Changed_Linger_Unit,
            _producer.Field_Max_Message_Size: _Changed_Max_Message_Size,
            _producer.Field_Max_Message_Size + Unit_Suffix: _Changed_Max_Message_Size_Unit,
        })

        batches_summary = _tab_summary(page, _Outconn_Page_Prefix, 'create', 'producer', _Line_Batches)
        assert 'Gathered for' in batches_summary, batches_summary

        switch_to_tab(page, _Outconn_Page_Prefix, 'create')
        click_switch(page, 'create', Field_Use_Queue)
        set_popover_values(page, _Outconn_Page_Prefix, 'create', Line_Retries, {
            Field_Max_Retries: _Changed_Max_Retries,
            Field_Sleep_Time: _Changed_Sleep_Time,
            Field_Sleep_Time + Unit_Suffix: _Changed_Sleep_Time_Unit,
        })

        submit_create_form(page)
        _ = wait_for_kafka_outconn_row(page, name)

        stored = _get_stored(api_client, _Outconn_Type, name)

        assert stored[_producer.Field_Compression] == _Changed_Compression
        assert stored[_producer.Field_Linger_Ms] == _Changed_Linger_Ms
        assert stored[_producer.Field_Max_Message_Size] == _Changed_Max_Message_Size_Bytes
        assert stored[_producer.Field_Acks] == _producer.Default_Acks
        assert stored[_producer.Field_Is_Idempotent] is True
        assert stored['use_queue'] is True
        assert stored['max_retries'] == int(_Changed_Max_Retries)
        assert stored['retry_sleep_time'] == _Changed_Sleep_Time_Seconds

        outconn_id = get_kafka_outconn_id(page, name)
        open_outconn_edit_dialog(page, outconn_id)

        assert _tab_names(page, 'edit') == _Outconn_Tab_Order, _tab_names(page, 'edit')

        _switch_to_tab(page, _Outconn_Page_Prefix, 'edit', 'producer')
        assert _field_value(page, 'edit', _producer.Field_Compression) == _Changed_Compression
        assert _field_value(page, 'edit', _producer.Field_Linger_Ms) == _Changed_Linger
        assert _field_value(page, 'edit', _producer.Field_Linger_Ms + Unit_Suffix) == _Changed_Linger_Unit
        assert _field_value(page, 'edit', _producer.Field_Max_Message_Size) == _Changed_Max_Message_Size
        assert _field_value(page, 'edit', _producer.Field_Max_Message_Size + Unit_Suffix) == _Changed_Max_Message_Size_Unit

        # One Kafka instance to confirm, waited for longer
        _set_tab_popover_values(page, _Outconn_Page_Prefix, 'edit', 'producer', _Line_Acks, _Producer_Popover_Prefix, {
            _producer.Field_Acks: _Changed_Acks,
            _producer.Field_Send_Timeout: _Changed_Send_Timeout,
            _producer.Field_Send_Timeout + Unit_Suffix: _Changed_Send_Timeout_Unit,
        })

        acks_summary = _tab_summary(page, _Outconn_Page_Prefix, 'edit', 'producer', _Line_Acks)
        assert 'One Kafka instance' in acks_summary, acks_summary

        switch_to_tab(page, _Outconn_Page_Prefix, 'edit')
        assert is_checked(page, 'edit', Field_Use_Queue)
        assert get_field_value(page, 'edit', Field_Max_Retries) == _Changed_Max_Retries
        assert get_field_value(page, 'edit', Field_Sleep_Time) == _Changed_Sleep_Time
        assert get_field_value(page, 'edit', Field_Sleep_Time + Unit_Suffix) == _Changed_Sleep_Time_Unit

        set_popover_values(page, _Outconn_Page_Prefix, 'edit', Line_Action, {
            Field_Action: _dlq.Action.Discard,
        })
        assert summary_text(page, _Outconn_Page_Prefix, 'edit', Line_Action) == 'Discard'

        submit_edit_form(page)

        stored = _get_stored(api_client, _Outconn_Type, name)

        assert stored[_producer.Field_Acks] == _Changed_Acks
        assert stored[_producer.Field_Send_Timeout] == _Changed_Send_Timeout_Seconds
        assert stored[_producer.Field_Compression] == _Changed_Compression
        assert stored['dlq_action'] == _dlq.Action.Discard
        assert stored['max_retries'] == int(_Changed_Max_Retries)

        delete_kafka_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################

class TestKafkaChannelTabs:

    def test_create_dialog_has_the_consumer_routing_and_delivery_tabs(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
    ) -> 'None':
        """ The channel dialog has the Config, Consumer, Routing and Delivery tabs, the Consumer tab reads its defaults,
        the Routing tab starts empty and the Delivery tab has no queue switch, with the DLQ in force.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _open_channel_create_dialog(page, base_url, _Test_Name_Prefix + 'channel.tabs', _Topics_Lines[0])
        assert _tab_names(page, 'create') == _Channel_Tab_Order, _tab_names(page, 'create')

        _switch_to_tab(page, _Channel_Page_Prefix, 'create', 'consumer')

        assert _field_value(page, 'create', _consumer.Field_Auto_Offset_Reset) == _consumer.Default_Auto_Offset_Reset
        assert _field_value(page, 'create', _consumer.Field_Max_In_Flight) == str(_consumer.Default_Max_In_Flight)
        assert _field_value(page, 'create', _consumer.Field_Dedup_Header) == _consumer.Default_Dedup_Header
        assert not page.is_checked(f'#{_field_id("create", _consumer.Field_Should_Deliver_Tombstones)}')

        _switch_to_tab(page, _Channel_Page_Prefix, 'create', 'routing')
        assert _routing_rules(page, 'create') == []
        assert _routing_rule_count(page, 'create') == 0
        assert page.is_visible(f'#{_tab_panel_id(_Channel_Page_Prefix, "create", "routing")}-rules .kafka-routing-tab-empty')

        switch_to_tab(page, _Channel_Page_Prefix, 'create')

        assert not page.is_visible(f'#{panel_id(_Channel_Page_Prefix, "create")}-line-use_queue')
        assert not panel_is_off(page, _Channel_Page_Prefix, 'create')
        assert is_checked(page, 'create', Field_Use_DLQ)
        assert summary_text(page, _Channel_Page_Prefix, 'create', Line_Action) == 'Keep in DLQ'

        close_dialog_via_jquery(page, 'create-div')

# ################################################################################################################################

    def test_create_and_edit_store_the_topics_consumer_routing_and_delivery_settings(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
    ) -> 'None':
        """ Topics given one per line, the Consumer tab, the rules of the Routing tab and the Delivery tab are stored
        the way the dialog set them, the edit dialog reads them back and an edit with comma-separated topics stores the changes.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Test_Name_Prefix + 'channel.store'

        _open_channel_create_dialog(page, base_url, name, '\n'.join(_Topics_Lines))

        _switch_to_tab(page, _Channel_Page_Prefix, 'create', 'consumer')
        _set_select(page, 'create', _consumer.Field_Auto_Offset_Reset, _Changed_Auto_Offset_Reset)

        _set_tab_popover_values(page, _Channel_Page_Prefix, 'create', 'consumer', _Line_Limits, _Consumer_Popover_Prefix, {
            _consumer.Field_Max_In_Flight: _Changed_Max_In_Flight,
        })

        _set_tab_popover_values(page, _Channel_Page_Prefix, 'create', 'consumer', _Line_Dedup, _Consumer_Popover_Prefix, {
            _consumer.Field_Dedup_Header: _Changed_Dedup_Header,
            _consumer.Field_Dedup_TTL: _Changed_Dedup_TTL,
            _consumer.Field_Dedup_TTL + Unit_Suffix: _Changed_Dedup_TTL_Unit,
        })

        dedup_summary = _tab_summary(page, _Channel_Page_Prefix, 'create', 'consumer', _Line_Dedup)
        assert _Changed_Dedup_Header in dedup_summary, dedup_summary

        _switch_to_tab(page, _Channel_Page_Prefix, 'create', 'routing')
        _add_routing_rule(page, 'create', _Topics_Lines[0], 'X-Kind', 'priority', _Routing_Service)
        _add_routing_rule(page, 'create', '', 'X-Kind', '', _Routing_Service)

        assert _routing_rule_count(page, 'create') == 2
        assert _routing_rules(page, 'create') == [
            {
                _routing.Key_Topic: _Topics_Lines[0],
                _routing.Key_Header_Name: 'X-Kind',
                _routing.Key_Header_Value: 'priority',
                _routing.Key_Service: _Routing_Service,
            },
            {
                _routing.Key_Topic: '',
                _routing.Key_Header_Name: 'X-Kind',
                _routing.Key_Header_Value: '',
                _routing.Key_Service: _Routing_Service,
            },
        ]

        switch_to_tab(page, _Channel_Page_Prefix, 'create')
        set_popover_values(page, _Channel_Page_Prefix, 'create', Line_Retries, {
            Field_Max_Retries: _Changed_Max_Retries,
            Field_Sleep_Time: _Changed_Sleep_Time,
            Field_Sleep_Time + Unit_Suffix: _Changed_Sleep_Time_Unit,
        })
        set_popover_values(page, _Channel_Page_Prefix, 'create', Line_Action, {
            Field_Action: _dlq.Action.Discard,
        })

        submit_create_form(page)
        _ = wait_for_kafka_channel_row(page, name)

        stored = _get_stored(api_client, _Channel_Type, name)

        assert stored[_consumer.Field_Topics].split() == _Topics_Lines, stored[_consumer.Field_Topics]
        assert stored[_consumer.Field_Auto_Offset_Reset] == _Changed_Auto_Offset_Reset
        assert stored[_consumer.Field_Max_In_Flight] == int(_Changed_Max_In_Flight)
        assert stored[_consumer.Field_Dedup_Header] == _Changed_Dedup_Header
        assert stored[_consumer.Field_Dedup_TTL] == _Changed_Dedup_TTL_Seconds
        assert stored['max_retries'] == int(_Changed_Max_Retries)
        assert stored['retry_sleep_time'] == _Changed_Sleep_Time_Seconds
        assert stored['dlq_action'] == _dlq.Action.Discard

        stored_rules = json.loads(stored[_consumer.Field_Routing])
        assert len(stored_rules) == 2
        assert stored_rules[0][_routing.Key_Topic] == _Topics_Lines[0]
        assert stored_rules[0][_routing.Key_Header_Value] == 'priority'
        assert stored_rules[1][_routing.Key_Header_Name] == 'X-Kind'
        assert stored_rules[1][_routing.Key_Service] == _Routing_Service

        # The list shows the topics as one line
        row = find_kafka_channel_row(page, name)
        assert ', '.join(_Topics_Lines) in row.inner_text()

        channel_id = get_kafka_channel_id(page, name)
        open_channel_edit_dialog(page, channel_id)

        assert _tab_names(page, 'edit') == _Channel_Tab_Order, _tab_names(page, 'edit')
        assert _field_value(page, 'edit', _consumer.Field_Topics).split() == _Topics_Lines

        _switch_to_tab(page, _Channel_Page_Prefix, 'edit', 'consumer')
        assert _field_value(page, 'edit', _consumer.Field_Auto_Offset_Reset) == _Changed_Auto_Offset_Reset
        assert _field_value(page, 'edit', _consumer.Field_Max_In_Flight) == _Changed_Max_In_Flight
        assert _field_value(page, 'edit', _consumer.Field_Dedup_Header) == _Changed_Dedup_Header
        assert _field_value(page, 'edit', _consumer.Field_Dedup_TTL) == _Changed_Dedup_TTL
        assert _field_value(page, 'edit', _consumer.Field_Dedup_TTL + Unit_Suffix) == _Changed_Dedup_TTL_Unit

        _switch_to_tab(page, _Channel_Page_Prefix, 'edit', 'routing')
        assert _routing_rule_count(page, 'edit') == 2

        # The first rule goes, the second one moves up
        page.click(f'#{_tab_panel_id(_Channel_Page_Prefix, "edit", "routing")}-rule-0 .kafka-routing-tab-delete')
        assert _routing_rule_count(page, 'edit') == 1
        assert _routing_rules(page, 'edit')[0][_routing.Key_Topic] == ''

        switch_to_tab(page, _Channel_Page_Prefix, 'edit')
        assert not page.is_visible(f'#{panel_id(_Channel_Page_Prefix, "edit")}-line-use_queue')
        assert get_field_value(page, 'edit', Field_Max_Retries) == _Changed_Max_Retries
        assert get_field_value(page, 'edit', Field_Action) == _dlq.Action.Discard

        # Comma-separated topics on the edit
        fill_kafka_channel_form(page, {'topics': ', '.join(_Topics_Edited)}, 'edit-')
        submit_edit_form(page)

        stored = _get_stored(api_client, _Channel_Type, name)

        assert stored[_consumer.Field_Topics].replace(',', ' ').split() == _Topics_Edited, stored[_consumer.Field_Topics]
        assert len(json.loads(stored[_consumer.Field_Routing])) == 1
        assert stored[_consumer.Field_Auto_Offset_Reset] == _Changed_Auto_Offset_Reset

        _ = wait_for_kafka_channel_row(page, name)
        row = find_kafka_channel_row(page, name)
        assert ', '.join(_Topics_Edited) in row.inner_text()

        delete_kafka_channel(page, channel_id)

# ################################################################################################################################

    def test_the_list_links_to_the_dlq_page_of_a_channel(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
    ) -> 'None':
        """ Each channel's row links to its DLQ page, which shows the DLQ alone, with no queue tab.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        name = _Test_Name_Prefix + 'channel.dlq'

        channel_id = create_kafka_channel(page, base_url, name, {
            'address': _Address,
            'topics': _Topics_Lines[0],
            'group_id': name,
            'service': _Channel_Service,
        })

        expected_url = _Channel_DLQ_URL.format(conn_type=_Channel_DLQ_Conn_Type, conn_id=channel_id)

        row = find_kafka_channel_row(page, name)
        link = row.query_selector('td.kafka-channel-dlq-cell a')
        assert link is not None, row.inner_html()
        assert link.text_content().strip() == 'Dead-letter queue'
        assert link.get_attribute('href').replace('&amp;', '&') == expected_url

        link.click()
        _ = page.wait_for_selector('#delivery-tab-panel-dlq', state='visible', timeout=10000)

        assert expected_url.split('?')[0] in page.url
        assert page.inner_text('#markup h2.zato').strip() == f'Delivery: {name}'

        tab_names = page.eval_on_selector_all('.delivery-tabs .dashboard-tab', 'items => items.map(item => item.dataset.tab)')
        assert tab_names == ['dlq'], tab_names

        assert page.query_selector('#delivery-tab-panel-queue') is None
        assert page.is_visible('#delivery-table-dlq')

        delete_kafka_channel(page, channel_id)

# ################################################################################################################################
# ################################################################################################################################
