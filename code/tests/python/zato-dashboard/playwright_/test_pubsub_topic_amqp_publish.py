# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sqlite3
import tempfile
import time
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.test.client import PublishClient
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_amqp_topic, create_basic_auth, \
    create_outgoing_amqp, create_outgoing_rest_with_address, create_permission, create_push_rest_subscription, \
    create_rest_channel, get_item_id, navigate_to_page, open_publish_overlay, publish_via_overlay
from zato.common.test.rabbitmq_ import declare_and_bind, drain_queue
from zato.common.test.receiver import WebhookReceiver
from zato.common.util.api import new_cid

# The broker fixture is resolved by pytest through this import
from amqp_fixtures import deploy_service, rabbitmq_broker # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.amqp.publish.' + new_cid() + '.'

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# How long the config event needs to reach the runtime registry after a form submission
_Config_Propagation_Delay = 1.0

# The standard prefix of pub/sub message IDs
_Msg_Id_Prefix = 'zpsm'

# ################################################################################################################################
# ################################################################################################################################

def _get_broker_address(broker_config:'anydict') -> 'str':
    """ Returns the address of the private broker in the format AMQP connection forms expect.
    """
    amqp_port = broker_config['amqp_port']
    out = f'amqp://127.0.0.1:{amqp_port}//'
    return out

# ################################################################################################################################

def _create_amqp_topic_for_queue(
    page:'Page',
    base_url:'str',
    broker_config:'anydict',
    suffix:'str',
    ) -> 'anydict':
    """ Creates an outgoing connection and an AMQP topic whose routing key matches
    the fixture queue's binding, so publishes land on that queue.
    """
    outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
    topic_name = _Test_Name_Prefix + 'topic.' + suffix

    address = _get_broker_address(broker_config)

    _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

    item_id = create_amqp_topic(
        page, base_url, topic_name, outconn_name, broker_config['exchange'], broker_config['routing_key'], '')

    # Let the config event reach the runtime registry before anything is published
    time.sleep(_Config_Propagation_Delay)

    out = {
        'topic_name': topic_name,
        'item_id': item_id,
        'outconn_name': outconn_name,
    }

    return out

# ################################################################################################################################

def _count_topic_message_rows(pubsub_db_path:'str', topic_name:'str') -> 'int':
    """ Counts one topic's message rows in the server's pub/sub database.
    """
    connection = sqlite3.connect(pubsub_db_path)

    try:
        cursor = connection.execute(
            'SELECT COUNT(*) FROM pubsub_message WHERE topic_name = ?', (topic_name.lower(),))
        row = cursor.fetchone()
    finally:
        connection.close()

    out = row[0]
    return out

# ################################################################################################################################

def _post_json(url:'str', payload:'anydict') -> 'anydict':
    """ POSTs a JSON payload to a URL and returns the parsed JSON response.
    """
    body = json.dumps(payload).encode()

    request = Request(url, data=body, method='POST')
    request.add_header('Content-Type', 'application/json')

    with urlopen(request) as response:
        raw = response.read()

    out = json.loads(raw)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def publisher_service(zato_dashboard:'anydict') -> 'anydict':
    """ Hot-deploys a service whose handler calls self.publish, for the tests
    that publish from within the server.
    """
    service_name = 'test.amqp.publisher.' + new_cid()

    source = f'''# -*- coding: utf-8 -*-

# stdlib
from json import dumps, loads

# Zato
from zato.server.service import Service

class AMQPTestPublisher(Service):
    name = '{service_name}'

    def handle(self):
        request = loads(self.request.raw_request)
        result = self.publish(request['topic_name'], request['data'])
        self.response.payload = dumps({{'is_ok': True, 'msg_id': result.msg_id}})
'''

    file_path = deploy_service(zato_dashboard['server_dir'], '_test_amqp_publisher.py', source)

    yield {
        'service_name': service_name,
    }

    # Remove the deployed file on teardown
    if os.path.exists(file_path):
        os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicAMQPPublish:
    """ Publish-side tests for AMQP-backed pub/sub topics against a real RabbitMQ broker.
    """

    def test_overlay_publish_lands_on_queue(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A message published through the invoker overlay lands on the bound RabbitMQ queue.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Make sure nothing is left on the queue from previous activity ..
        _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

        # .. configure the outgoing connection and topic via forms ..
        topic_info = _create_amqp_topic_for_queue(page, base_url, rabbitmq_broker, 'overlay')

        # .. publish through the overlay ..
        payload = 'overlay-payload-' + new_cid()

        open_publish_overlay(page, topic_info['item_id'])
        publish_via_overlay(page, payload)

        # .. and the queue holds exactly that one message.
        messages = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'])

        assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
        assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################

    def test_rest_publish_lands_on_queue(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A message published through the pub/sub REST endpoint by an external client
        lands on the bound RabbitMQ queue and the response carries is_ok and a msg_id.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Make sure nothing is left on the queue from previous activity ..
        _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

        # .. configure the outgoing connection and topic via forms ..
        topic_info = _create_amqp_topic_for_queue(page, base_url, rabbitmq_broker, 'rest')
        topic_name = topic_info['topic_name']

        # .. the external publisher needs a security definition and a publisher permission ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'rest')
        _ = create_permission(page, base_url, sec_info['name'], 'publisher', 'pub', topic_name)

        # .. publish as an external REST client would ..
        server_port = zato_dashboard['server_port']
        client = PublishClient(f'http://127.0.0.1:{server_port}', sec_info['username'], sec_info['password'])

        payload = 'rest-payload-' + new_cid()
        response = client.publish(topic_name, payload)

        # .. the response carries is_ok and a msg_id with the standard prefix ..
        assert response['is_ok'] is True, f'Expected is_ok, got: {response}'
        assert response['msg_id'].startswith(_Msg_Id_Prefix), f'Expected a `{_Msg_Id_Prefix}` msg_id, got: {response}'

        # .. and the queue holds exactly that one message.
        messages = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'])

        assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
        assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################

    def test_self_publish_lands_on_queue(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        publisher_service:'anydict',
        ) -> 'None':
        """ A message published with self.publish from a hot-deployed service
        lands on the bound RabbitMQ queue and the service returns the PublishResult fields.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Make sure nothing is left on the queue from previous activity ..
        _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

        # .. configure the outgoing connection and topic via forms ..
        topic_info = _create_amqp_topic_for_queue(page, base_url, rabbitmq_broker, 'selfpub')
        topic_name = topic_info['topic_name']

        # .. the publisher service is reached through a REST channel created in the dashboard ..
        service_name = publisher_service['service_name']

        channel_name = _Test_Name_Prefix + 'channel.rest.37'
        url_path = '/test/amqp/publisher/' + new_cid()

        create_rest_channel(page, base_url, channel_name, service_name, url_path)

        # .. call the channel the way its users would ..
        server_port = zato_dashboard['server_port']
        payload = 'service-payload-' + new_cid()

        response = _post_json(f'http://127.0.0.1:{server_port}{url_path}', {
            'topic_name': topic_name,
            'data': payload,
        })

        # .. the service returned the PublishResult fields ..
        assert response['is_ok'] is True, f'Expected is_ok, got: {response}'
        assert response['msg_id'].startswith(_Msg_Id_Prefix), f'Expected a `{_Msg_Id_Prefix}` msg_id, got: {response}'

        # .. and the queue holds exactly that one message.
        messages = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'])

        assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
        assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################

    def test_overlay_history_shows_msg_id(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ The overlay's history panel shows the msg_id returned by an AMQP publish.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the outgoing connection and topic via forms ..
        topic_info = _create_amqp_topic_for_queue(page, base_url, rabbitmq_broker, 'history')

        # .. publish through the overlay ..
        open_publish_overlay(page, topic_info['item_id'])
        publish_via_overlay(page, 'history-payload-' + new_cid())

        # .. open the history panel ..
        page.click('#invoker-modal-history-button')
        page.wait_for_selector('#invoker-modal-history-overlay:not(.hidden)', state='visible', timeout=5000)

        # .. show the response of the first entry ..
        show_response = page.query_selector(
            '#invoker-modal-history-list .invoker-history-item-wrapper:first-child .invoker-history-item-show-response')
        show_response.click()
        time.sleep(0.3)

        # .. and the msg_id with the standard prefix is in it.
        response_detail = page.query_selector('.invoker-history-response-detail.visible')
        response_text = response_detail.inner_text()

        assert 'msg_id' in response_text, f'Expected `msg_id` in the response detail, got: {response_text}'
        assert _Msg_Id_Prefix in response_text, f'Expected a `{_Msg_Id_Prefix}` msg_id in the response detail, got: {response_text}'

        # .. leave the queue clean for the next test.
        _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

# ################################################################################################################################

    def test_custom_routing_key_honored(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A topic with an explicit routing key delivers to a queue bound with that key
        and not to a queue bound with the topic name.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = 'customkey'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        address = _get_broker_address(rabbitmq_broker)

        # Two queues - one bound with the custom key, one bound with the topic name ..
        custom_key = 'custom.key.' + new_cid()
        custom_queue = 'custom.queue.' + new_cid()
        topic_name_queue = 'topic.name.queue.' + new_cid()

        declare_and_bind(amqp_url, exchange, custom_queue, custom_key)
        declare_and_bind(amqp_url, exchange, topic_name_queue, topic_name)

        # .. configure the topic with the custom routing key via forms ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)
        item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, custom_key, '')

        time.sleep(_Config_Propagation_Delay)

        # .. publish through the overlay ..
        payload = 'custom-key-payload-' + new_cid()

        open_publish_overlay(page, item_id)
        publish_via_overlay(page, payload)

        # .. the custom-key queue received the message ..
        custom_messages = drain_queue(amqp_url, custom_queue)

        assert len(custom_messages) == 1, f'Expected exactly one message, got: {custom_messages}'
        assert custom_messages[0] == payload, f'Expected `{payload}`, got `{custom_messages[0]}`'

        # .. and the topic-name queue received nothing.
        topic_name_messages = drain_queue(amqp_url, topic_name_queue, timeout=1)
        assert not topic_name_messages, f'Expected no messages, got: {topic_name_messages}'

# ################################################################################################################################

    def test_default_routing_key_is_topic_name(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A topic without a routing key delivers to a queue bound with the topic name.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        suffix = 'defaultkey'
        outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
        topic_name = _Test_Name_Prefix + 'topic.' + suffix

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        address = _get_broker_address(rabbitmq_broker)

        # A queue bound with the topic name as the key ..
        topic_name_queue = 'topic.name.queue.' + new_cid()
        declare_and_bind(amqp_url, exchange, topic_name_queue, topic_name)

        # .. configure the topic with the routing key left empty ..
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)
        item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, '', '')

        time.sleep(_Config_Propagation_Delay)

        # .. publish through the overlay ..
        payload = 'default-key-payload-' + new_cid()

        open_publish_overlay(page, item_id)
        publish_via_overlay(page, payload)

        # .. and the queue bound with the topic name received the message.
        messages = drain_queue(amqp_url, topic_name_queue)

        assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
        assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################

    def test_no_database_rows_for_amqp_topic(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Publishing to an AMQP-backed topic leaves no rows in the pub/sub database -
        the broker owns the storage of such topics.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the outgoing connection and topic via forms ..
        topic_info = _create_amqp_topic_for_queue(page, base_url, rabbitmq_broker, 'nodatabase')
        topic_name = topic_info['topic_name']

        # .. publish through the overlay ..
        open_publish_overlay(page, topic_info['item_id'])
        publish_via_overlay(page, 'database-check-payload-' + new_cid())

        # .. and the server's pub/sub database holds no rows for the AMQP topic.
        row_count = _count_topic_message_rows(zato_dashboard['pubsub_db_path'], topic_name)
        assert row_count == 0, f'Expected no message rows for `{topic_name}`, got: {row_count}'

        # .. leave the queue clean for the next test.
        _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

# ################################################################################################################################

    def test_builtin_topic_still_delivered_via_push(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':
        """ A built-in topic with a REST push subscriber still delivers through
        the normal push path, both backends coexist in one server.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # A local receiver stands in for the user's push endpoint ..
        receiver_port = find_free_port()
        output_directory = tempfile.mkdtemp(prefix='zato_test_amqp_42_')

        receiver = WebhookReceiver(receiver_port, output_directory)
        receiver.start()

        try:
            # .. sec def, built-in topic and subscriber permission via forms ..
            prereqs = create_all_subscription_prerequisites(page, base_url, _Test_Name_Prefix, 'builtinpush')
            topic_name = prereqs['topic_name']
            sec_name = prereqs['sec_name']

            # .. an outgoing REST connection pointing at the receiver ..
            rest_name = _Test_Name_Prefix + 'rest.42'
            create_outgoing_rest_with_address(page, base_url, rest_name, f'http://127.0.0.1:{receiver_port}', '/push')

            # .. a push subscription targeting it ..
            create_push_rest_subscription(page, base_url, sec_name, topic_name, rest_name)

            time.sleep(_Config_Propagation_Delay)

            # .. publish through the overlay ..
            navigate_to_page(page, base_url, _Topic_Page_Url)
            item_id = get_item_id(page, topic_name)

            payload_marker = 'builtin-push-payload-' + new_cid()

            open_publish_overlay(page, item_id)
            publish_via_overlay(page, payload_marker)

            # .. and the receiver got the message through the push path.
            messages = receiver.wait_for_delivery(1)

            assert len(messages) >= 1, f'Expected at least one delivery, got: {messages}'

            serialized = json.dumps(messages)
            assert payload_marker in serialized, f'Expected `{payload_marker}` in deliveries, got: {serialized}'

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################
