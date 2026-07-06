# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.playwright_pubsub import collect_console_errors, collect_http_errors, confirm_delete, \
    create_amqp_channel, create_amqp_topic, create_outgoing_amqp, create_topic, filter_console_noise, find_row_by_name, \
    navigate_to_page, open_create_dialog, open_edit_and_read_backend_fields, open_edit_dialog, \
    set_select_value, submit_edit_form, trigger_delete
from zato.common.util.api import new_cid

# The broker fixture is resolved by pytest through this import
from amqp_fixtures import rabbitmq_broker # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.amqp.config.' + new_cid() + '.'

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# The service AMQP channels invoke when the tests do not care about the target
_Default_Channel_Service = 'demo.ping'

# ################################################################################################################################
# ################################################################################################################################

def _get_broker_address(broker_config:'anydict') -> 'str':
    """ Returns the address of the private broker in the format AMQP connection forms expect.
    """
    amqp_port = broker_config['amqp_port']
    out = f'amqp://127.0.0.1:{amqp_port}//'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicAMQPConfig:
    """ Dashboard configuration tests for AMQP-backed pub/sub topics.
    """

    def test_24_create_outgoing_amqp_via_form(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 24 - an outgoing AMQP connection created through the form appears in the table
        and the edit dialog shows the stored address.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'outconn.24'
        address = _get_broker_address(rabbitmq_broker)

        # Create the connection through the form ..
        item_id = create_outgoing_amqp(page, base_url, name, address, _Broker_Username, _Broker_Password)

        # .. the row is in the table ..
        row = find_row_by_name(page, name)
        assert row is not None, f'Row for `{name}` not found'

        # .. and the edit dialog shows the stored address.
        page.evaluate(f'$.fn.zato.outgoing.amqp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        stored_address = page.input_value('#id_edit-address')
        assert stored_address == address, f'Expected address `{address}`, got `{stored_address}`'

        stored_username = page.input_value('#id_edit-username')
        assert stored_username == _Broker_Username, f'Expected username `{_Broker_Username}`, got `{stored_username}`'

# ################################################################################################################################

    def test_25_create_amqp_channel_via_form(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 25 - an AMQP channel created through the form appears in the table
        and the edit dialog shows the stored values.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'channel.25'
        address = _get_broker_address(rabbitmq_broker)
        queue = rabbitmq_broker['queue']

        # Create the channel through the form ..
        item_id = create_amqp_channel(
            page, base_url, name, address, _Broker_Username, _Broker_Password, queue, _Default_Channel_Service)

        # .. the row is in the table ..
        row = find_row_by_name(page, name)
        assert row is not None, f'Row for `{name}` not found'

        # .. and the edit dialog shows the stored values.
        page.evaluate(f'$.fn.zato.channel.amqp.edit("{item_id}")')
        page.wait_for_selector('#edit-div', state='visible', timeout=5000)

        stored_address = page.input_value('#id_edit-address')
        assert stored_address == address, f'Expected address `{address}`, got `{stored_address}`'

        stored_queue = page.input_value('#id_edit-queue')
        assert stored_queue == queue, f'Expected queue `{queue}`, got `{stored_queue}`'

        stored_service = page.input_value('#id_edit-service')
        assert stored_service == _Default_Channel_Service, \
            f'Expected service `{_Default_Channel_Service}`, got `{stored_service}`'

# ################################################################################################################################

    def test_26_create_dialog_defaults_to_builtin(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Item 26 - the topic create dialog defaults to the built-in backend
        and all four AMQP inputs are hidden.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the create dialog ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        open_create_dialog(page)

        # .. the backend type shows builtin ..
        backend_type = page.input_value('#id_backend_type')
        assert backend_type == 'builtin', f'Expected `builtin`, got `{backend_type}`'

        # .. and every AMQP row is hidden.
        amqp_rows = page.query_selector_all('.zato-topic-amqp-row-create')
        assert len(amqp_rows) == 4, f'Expected 4 AMQP rows, got {len(amqp_rows)}'

        for amqp_row in amqp_rows:
            assert not amqp_row.is_visible(), 'Expected the AMQP row to be hidden with the built-in backend'

# ################################################################################################################################

    def test_27_backend_select_toggles_amqp_fields(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Item 27 - selecting AMQP reveals the AMQP inputs, switching back to built-in hides them.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the create dialog ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        open_create_dialog(page)

        # .. select the AMQP backend ..
        set_select_value(page, '#id_backend_type', 'amqp')
        page.wait_for_selector('.zato-topic-amqp-row-create', state='visible', timeout=5000)

        # .. all four AMQP rows are now visible ..
        amqp_rows = page.query_selector_all('.zato-topic-amqp-row-create')

        for amqp_row in amqp_rows:
            assert amqp_row.is_visible(), 'Expected the AMQP row to be visible with the AMQP backend'

        # .. switch back to built-in ..
        set_select_value(page, '#id_backend_type', 'builtin')
        page.wait_for_selector('.zato-topic-amqp-row-create', state='hidden', timeout=5000)

        # .. and the rows are hidden again.
        for amqp_row in amqp_rows:
            assert not amqp_row.is_visible(), 'Expected the AMQP row to be hidden again with the built-in backend'

# ################################################################################################################################

    def test_28_create_amqp_topic_via_form(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 28 - an AMQP topic created through the form appears in the table
        and the edit dialog shows exactly what was entered.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = '28'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        exchange = rabbitmq_broker['exchange']
        routing_key = rabbitmq_broker['routing_key']
        address = _get_broker_address(rabbitmq_broker)

        # The topic needs an outgoing connection to point to ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. create the topic through the form ..
        item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, routing_key, '')

        # .. the row shows the AMQP badge ..
        row = find_row_by_name(page, topic_name)
        row_html = row.inner_html()
        assert 'zato-topic-backend-badge-amqp' in row_html, f'Expected the AMQP badge in row: {row_html}'

        # .. and the edit dialog shows every value that was entered.
        fields = open_edit_and_read_backend_fields(page, item_id)

        assert fields['backend_type'] == 'amqp', f'Expected `amqp`, got `{fields["backend_type"]}`'
        assert fields['amqp_outconn_name'] == outconn_name, f'Expected `{outconn_name}`, got `{fields["amqp_outconn_name"]}`'
        assert fields['amqp_exchange'] == exchange, f'Expected `{exchange}`, got `{fields["amqp_exchange"]}`'
        assert fields['amqp_routing_key'] == routing_key, f'Expected `{routing_key}`, got `{fields["amqp_routing_key"]}`'
        assert fields['amqp_channel_name'] == '', f'Expected an empty channel, got `{fields["amqp_channel_name"]}`'

# ################################################################################################################################

    def test_29_empty_routing_key_shows_topic_name_on_edit(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 29 - a topic created with an empty routing key stores the topic name in it,
        which the edit dialog then shows.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = '29'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        exchange = rabbitmq_broker['exchange']
        address = _get_broker_address(rabbitmq_broker)

        # The topic needs an outgoing connection to point to ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. create the topic with the routing key left empty ..
        item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, '', '')

        # .. and the edit dialog shows the topic name as the routing key.
        fields = open_edit_and_read_backend_fields(page, item_id)

        assert fields['amqp_routing_key'] == topic_name, \
            f'Expected the topic name `{topic_name}` as the routing key, got `{fields["amqp_routing_key"]}`'

# ################################################################################################################################

    def test_30_missing_outconn_blocks_submission(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 30 - an AMQP topic without an outgoing connection cannot be submitted,
        the dialog stays open with a validation indication and no row is added.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        topic_name = _Test_Name_Prefix + 'topic.30'
        exchange = rabbitmq_broker['exchange']

        # Open the create dialog and pick the AMQP backend ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        open_create_dialog(page)

        page.fill('#id_name', topic_name)

        set_select_value(page, '#id_backend_type', 'amqp')
        page.wait_for_selector('.zato-topic-amqp-row-create', state='visible', timeout=5000)

        # .. fill in the exchange but leave the connection unselected ..
        page.fill('#id_amqp_exchange', exchange)

        # .. try to submit ..
        page.click('#create-div input[type="submit"]')

        # .. the required-field indicator appears and the dialog stays open ..
        indicator = page.wait_for_selector('#create-form .zato-name-invalid', state='visible', timeout=5000)
        indicator_text = indicator.inner_text()
        assert 'required' in indicator_text, f'Expected a required-field indication, got `{indicator_text}`'

        dialog = page.query_selector('#create-div')
        assert dialog.is_visible(), 'Expected the create dialog to stay open'

        # .. and no row was added.
        row = find_row_by_name(page, topic_name)
        assert row is None, f'Expected no row for `{topic_name}`'

# ################################################################################################################################

    def test_31_missing_exchange_blocks_submission(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 31 - an AMQP topic without an exchange cannot be submitted,
        the dialog stays open with a validation indication and no row is added.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = '31'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        address = _get_broker_address(rabbitmq_broker)

        # The connection exists so only the exchange is missing ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. open the create dialog and pick the AMQP backend ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        open_create_dialog(page)

        page.fill('#id_name', topic_name)

        set_select_value(page, '#id_backend_type', 'amqp')
        page.wait_for_selector('.zato-topic-amqp-row-create', state='visible', timeout=5000)

        # .. select the connection but leave the exchange empty ..
        set_select_value(page, '#id_amqp_outconn_name', outconn_name)

        # .. try to submit ..
        page.click('#create-div input[type="submit"]')

        # .. the required-field indicator appears and the dialog stays open ..
        indicator = page.wait_for_selector('#create-form .zato-name-invalid', state='visible', timeout=5000)
        indicator_text = indicator.inner_text()
        assert 'required' in indicator_text, f'Expected a required-field indication, got `{indicator_text}`'

        dialog = page.query_selector('#create-div')
        assert dialog.is_visible(), 'Expected the create dialog to stay open'

        # .. and no row was added.
        row = find_row_by_name(page, topic_name)
        assert row is None, f'Expected no row for `{topic_name}`'

# ################################################################################################################################

    def test_32_edit_builtin_to_amqp_and_back(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 32 - a built-in topic edited to AMQP stores the AMQP values,
        editing it back to built-in hides the AMQP inputs and requires no AMQP values.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = '32'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix

        exchange = rabbitmq_broker['exchange']
        address = _get_broker_address(rabbitmq_broker)

        # The topic needs an outgoing connection for its AMQP phase ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. create a built-in topic first ..
        topic_info = create_topic(page, base_url, _Test_Name_Prefix + 'topic.', suffix)
        topic_name = topic_info['name']
        item_id = topic_info['item_id']

        # .. edit it to AMQP ..
        open_edit_dialog(page, 'topic', item_id)

        set_select_value(page, '#id_edit-backend_type', 'amqp')
        page.wait_for_selector('.zato-topic-amqp-row-edit', state='visible', timeout=5000)

        set_select_value(page, '#id_edit-amqp_outconn_name', outconn_name)
        page.fill('#id_edit-amqp_exchange', exchange)

        submit_edit_form(page)

        # .. reopen the edit dialog and verify the AMQP values ..
        fields = open_edit_and_read_backend_fields(page, item_id)

        assert fields['backend_type'] == 'amqp', f'Expected `amqp`, got `{fields["backend_type"]}`'
        assert fields['amqp_outconn_name'] == outconn_name, f'Expected `{outconn_name}`, got `{fields["amqp_outconn_name"]}`'
        assert fields['amqp_exchange'] == exchange, f'Expected `{exchange}`, got `{fields["amqp_exchange"]}`'
        assert fields['amqp_routing_key'] == topic_name, f'Expected `{topic_name}`, got `{fields["amqp_routing_key"]}`'

        # .. edit back to built-in ..
        open_edit_dialog(page, 'topic', item_id)

        set_select_value(page, '#id_edit-backend_type', 'builtin')
        page.wait_for_selector('.zato-topic-amqp-row-edit', state='hidden', timeout=5000)

        # .. the AMQP rows are hidden and submission needs no AMQP values ..
        submit_edit_form(page)

        # .. and the topic is built-in again.
        fields = open_edit_and_read_backend_fields(page, item_id)
        assert fields['backend_type'] == 'builtin', f'Expected `builtin`, got `{fields["backend_type"]}`'

# ################################################################################################################################

    def test_33_full_crud_with_error_monitoring(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 33 - create, edit and delete an AMQP topic with zero console errors
        and zero HTTP 500s, server and dashboard logs are covered by the autouse fixture.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Attach the error monitors before doing anything ..
        console_errors = [] # type: list
        http_errors = [] # type: list

        collect_console_errors(page, console_errors)
        collect_http_errors(page, http_errors)

        suffix = '33'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        exchange = rabbitmq_broker['exchange']
        routing_key = rabbitmq_broker['routing_key']
        address = _get_broker_address(rabbitmq_broker)

        # .. create ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)
        item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, routing_key, '')

        # .. edit - change the exchange ..
        new_exchange = exchange + '.updated'

        open_edit_dialog(page, 'topic', item_id)
        page.fill('#id_edit-amqp_exchange', new_exchange)
        submit_edit_form(page)

        fields = open_edit_and_read_backend_fields(page, item_id)
        assert fields['amqp_exchange'] == new_exchange, f'Expected `{new_exchange}`, got `{fields["amqp_exchange"]}`'

        # .. delete ..
        trigger_delete(page, 'topic', item_id)
        confirm_delete(page)

        # .. the row is gone ..
        row = find_row_by_name(page, topic_name)
        assert row is None, f'Expected no row for `{topic_name}` after deletion'

        # .. and nothing went wrong along the way.
        real_console_errors = filter_console_noise(console_errors, ['favicon.ico'])

        assert not real_console_errors, f'Expected no console errors, got: {real_console_errors}'
        assert not http_errors, f'Expected no HTTP 500s, got: {http_errors}'

# ################################################################################################################################

    def test_34_builtin_create_flow_unaffected(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Item 34 - the plain built-in create flow still works with the new form elements present
        and built-in topics never show AMQP inputs.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a built-in topic exactly like the pre-AMQP flow does ..
        topic_info = create_topic(page, base_url, _Test_Name_Prefix + 'topic.builtin.', '34', 'A built-in topic')
        topic_name = topic_info['name']
        item_id = topic_info['item_id']

        # .. the row shows the built-in badge ..
        row = find_row_by_name(page, topic_name)
        row_html = row.inner_html()
        assert 'zato-topic-backend-badge-builtin' in row_html, f'Expected the built-in badge in row: {row_html}'

        # .. and its edit dialog keeps the AMQP inputs hidden.
        open_edit_dialog(page, 'topic', item_id)

        amqp_rows = page.query_selector_all('.zato-topic-amqp-row-edit')
        assert len(amqp_rows) == 4, f'Expected 4 AMQP rows, got {len(amqp_rows)}'

        for amqp_row in amqp_rows:
            assert not amqp_row.is_visible(), 'Expected the AMQP row to be hidden for a built-in topic'

# ################################################################################################################################
# ################################################################################################################################
