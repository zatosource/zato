# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
import time
from urllib.request import Request, urlopen

# kombu
from kombu import Connection

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.playwright_pubsub import confirm_delete, create_amqp_channel, create_amqp_topic, create_basic_auth, \
    create_outgoing_amqp, create_outgoing_rest_with_address, create_permission, create_push_rest_subscription, \
    create_push_service_subscription, create_rest_channel, find_row_by_name, open_edit_dialog, set_select_value, \
    submit_edit_form, trigger_delete
from zato.common.test.rabbitmq_ import declare_and_bind, get_queue_depth, publish_to_exchange
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

_Test_Name_Prefix = 'test.amqp.bridge.' + new_cid() + '.'

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# The service AMQP channels invoke when the tests do not care about the target
_Default_Channel_Service = 'demo.ping'

# How long the config event needs to reach the runtime registry after a form submission
_Config_Propagation_Delay = 1.0

# How long to wait for the channel's consumer to attach to its queue
_Consumer_Wait_Timeout = 30

# How long to wait for a file the marker service writes to
_File_Wait_Timeout = 30

# How long to wait for a queue to be fully drained and acked
_Queue_Drained_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def _get_broker_address(broker_config:'anydict') -> 'str':
    """ Returns the address of the private broker in the format AMQP connection forms expect.
    """
    amqp_port = broker_config['amqp_port']
    out = f'amqp://127.0.0.1:{amqp_port}//'
    return out

# ################################################################################################################################

def _wait_for_consumer(amqp_url:'str', queue:'str') -> 'None':
    """ Waits until at least one consumer is attached to a queue,
    which means the AMQP channel is ready to receive messages.
    """
    deadline = time.monotonic() + _Consumer_Wait_Timeout

    with Connection(amqp_url) as connection:
        channel = connection.channel()

        while time.monotonic() < deadline:
            declaration = channel.queue_declare(queue=queue, passive=True)

            if declaration.consumer_count > 0:
                return

            time.sleep(0.5)

    raise RuntimeError(f'No consumer attached to `{queue}` within {_Consumer_Wait_Timeout}s')

# ################################################################################################################################

def _wait_for_queue_drained(amqp_url:'str', queue:'str') -> 'int':
    """ Waits until a queue has no messages left, returning the final depth.
    """
    deadline = time.monotonic() + _Queue_Drained_Timeout

    depth = get_queue_depth(amqp_url, queue)

    while time.monotonic() < deadline:
        if depth == 0:
            break
        time.sleep(0.5)
        depth = get_queue_depth(amqp_url, queue)

    return depth

# ################################################################################################################################

def _wait_for_file_lines(file_path:'str', expected_count:'int') -> 'list':
    """ Waits until a file exists and has at least the expected number of lines, then returns them.
    """
    deadline = time.monotonic() + _File_Wait_Timeout

    while time.monotonic() < deadline:

        if os.path.exists(file_path):
            with open(file_path, 'r') as marker_file:
                lines = marker_file.read().splitlines()

            if len(lines) >= expected_count:
                return lines

        time.sleep(0.5)

    # The deadline passed - return whatever there is
    if os.path.exists(file_path):
        with open(file_path, 'r') as marker_file:
            out = marker_file.read().splitlines()
            return out

    return []

# ################################################################################################################################

def _read_receiver_raw(receiver:'WebhookReceiver') -> 'list':
    """ Returns the raw text of every payload the receiver persisted, without JSON parsing.
    """
    out = [] # type: list

    file_names = sorted(os.listdir(receiver.output_directory))

    for file_name in file_names:
        if not file_name.endswith('.json'):
            continue

        file_path = os.path.join(receiver.output_directory, file_name)

        with open(file_path, 'r') as payload_file:
            out.append(payload_file.read())

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

def _setup_amqp_pipeline(
    page:'Page',
    base_url:'str',
    broker_config:'anydict',
    suffix:'str',
    channel_service_name:'str',
    ) -> 'anydict':
    """ Configures the whole inbound pipeline via dashboard forms - a dedicated queue and binding,
    an outgoing connection, an AMQP channel consuming from the queue and an AMQP topic referencing
    the channel. Waits for the channel's consumer to attach before returning.
    """
    unique = new_cid()

    queue = f'bridge.queue.{suffix}.{unique}'
    binding_key = f'bridge.key.{suffix}.{unique}'

    amqp_url = broker_config['amqp_url']
    exchange = broker_config['exchange']
    address = _get_broker_address(broker_config)

    # The queue the channel will consume from ..
    declare_and_bind(amqp_url, exchange, queue, binding_key)

    # .. the outgoing connection for the publish side ..
    outconn_name = _Test_Name_Prefix + 'outconn.' + suffix
    _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

    # .. the channel for the inbound side ..
    channel_name = _Test_Name_Prefix + 'channel.' + suffix
    _ = create_amqp_channel(
        page, base_url, channel_name, address, _Broker_Username, _Broker_Password, queue, channel_service_name)

    # .. the topic that ties both sides together ..
    topic_name = _Test_Name_Prefix + 'topic.' + suffix
    item_id = create_amqp_topic(page, base_url, topic_name, outconn_name, exchange, binding_key, channel_name)

    # .. let the config event reach the runtime registry ..
    time.sleep(_Config_Propagation_Delay)

    # .. and make sure the consumer is ready before anything is injected.
    _wait_for_consumer(amqp_url, queue)

    out = {
        'topic_name': topic_name,
        'item_id': item_id,
        'outconn_name': outconn_name,
        'channel_name': channel_name,
        'queue': queue,
        'binding_key': binding_key,
    }

    return out

# ################################################################################################################################

def _add_rest_push_subscriber(
    page:'Page',
    base_url:'str',
    suffix:'str',
    topic_name:'str',
    receiver_port:'int',
    ) -> 'None':
    """ Configures a REST push subscriber for a topic via dashboard forms - a security definition,
    a subscriber permission, an outgoing REST connection pointing at the local receiver
    and the push subscription itself.
    """
    sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, suffix)
    sec_name = sec_info['name']

    _ = create_permission(page, base_url, sec_name, 'subscriber', 'sub', topic_name)

    rest_name = _Test_Name_Prefix + 'rest.' + suffix
    create_outgoing_rest_with_address(page, base_url, rest_name, f'http://127.0.0.1:{receiver_port}', '/push')

    create_push_rest_subscription(page, base_url, sec_name, topic_name, rest_name)

    time.sleep(_Config_Propagation_Delay)

# ################################################################################################################################

def _add_service_push_subscriber(
    page:'Page',
    base_url:'str',
    suffix:'str',
    topic_name:'str',
    service_name:'str',
    ) -> 'None':
    """ Configures a service push subscriber for a topic via dashboard forms.
    """
    sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, suffix)
    sec_name = sec_info['name']

    _ = create_permission(page, base_url, sec_name, 'subscriber', 'sub', topic_name)

    create_push_service_subscription(page, base_url, sec_name, topic_name, service_name)

    time.sleep(_Config_Propagation_Delay)

# ################################################################################################################################

def _deploy_file_writer_service(server_dir:'str', suffix:'str') -> 'anydict':
    """ Hot-deploys a service that appends every message it receives to a file.
    Returns the service name and the file path.
    """
    unique = new_cid()

    service_name = f'test.amqp.bridge.file-writer.{suffix}.{unique}'
    output_file = os.path.join(tempfile.gettempdir(), f'zato_test_amqp_bridge_{suffix}_{unique}.txt')

    source = f'''# -*- coding: utf-8 -*-

# stdlib
from json import dumps

# Zato
from zato.server.service import Service

class AMQPBridgeFileWriter(Service):
    name = '{service_name}'

    def handle(self):
        body = self.request.raw_request

        if isinstance(body, bytes):
            body = body.decode('utf8')
        elif not isinstance(body, str):
            body = dumps(body)

        with open('{output_file}', 'a') as marker_file:
            marker_file.write(body + chr(10))
'''

    file_path = deploy_service(server_dir, f'_test_amqp_bridge_writer_{suffix}.py', source)

    out = {
        'service_name': service_name,
        'output_file': output_file,
        'deployed_file': file_path,
    }

    return out

# ################################################################################################################################

def _deploy_publisher_service(server_dir:'str', suffix:'str') -> 'anydict':
    """ Hot-deploys a service whose handler calls self.publish with the topic name
    and data taken from the request. Returns the service name and the deployed file path.
    """
    unique = new_cid()

    service_name = f'test.amqp.bridge.publisher.{suffix}.{unique}'

    source = f'''# -*- coding: utf-8 -*-

# stdlib
from json import dumps, loads

# Zato
from zato.server.service import Service

class AMQPBridgePublisher(Service):
    name = '{service_name}'

    def handle(self):
        request = loads(self.request.raw_request)
        result = self.publish(request['topic_name'], request['data'])
        self.response.payload = dumps({{'is_ok': True, 'msg_id': result.msg_id}})
'''

    file_path = deploy_service(server_dir, f'_test_amqp_bridge_publisher_{suffix}.py', source)

    out = {
        'service_name': service_name,
        'deployed_file': file_path,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def webhook_receiver() -> 'WebhookReceiver':
    """ A local HTTP receiver standing in for the user's push endpoint.
    """
    receiver_port = find_free_port()
    output_directory = tempfile.mkdtemp(prefix='zato_test_amqp_bridge_')

    receiver = WebhookReceiver(receiver_port, output_directory)
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicAMQPBridge:
    """ Inbound bridge tests - messages injected into RabbitMQ are consumed by AMQP channels
    and delivered to the topic's push subscribers.
    """

    def test_43_rest_push_subscriber_receives_broker_message(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 43 - a message injected into the broker reaches a REST push subscriber through the bridge.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the pipeline and a REST push subscriber via forms ..
        pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '43', _Default_Channel_Service)
        _add_rest_push_subscriber(page, base_url, '43', pipeline['topic_name'], webhook_receiver.port)

        # .. inject a message the way an external AMQP producer would ..
        marker = 'bridge-rest-' + new_cid()
        body = json.dumps({'value': marker})

        publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

        # .. and the receiver got exactly that message.
        messages = webhook_receiver.wait_for_delivery(1)

        assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
        assert messages[0]['value'] == marker, f'Expected `{marker}`, got: {messages[0]}'

# ################################################################################################################################

    def test_44_service_push_subscriber_receives_broker_message(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 44 - a message injected into the broker reaches a service push subscriber through the bridge.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # A hot-deployed service writes each received message to a file ..
        writer = _deploy_file_writer_service(zato_dashboard['server_dir'], '44')

        try:
            # .. configure the pipeline and a service push subscriber via forms ..
            pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '44', _Default_Channel_Service)
            _add_service_push_subscriber(page, base_url, '44', pipeline['topic_name'], writer['service_name'])

            # .. inject a message ..
            marker = 'bridge-service-' + new_cid()
            body = json.dumps({'value': marker})

            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

            # .. and the service wrote it to its file.
            lines = _wait_for_file_lines(writer['output_file'], 1)

            assert len(lines) == 1, f'Expected exactly one line, got: {lines}'
            assert marker in lines[0], f'Expected `{marker}` in `{lines[0]}`'

        finally:
            if os.path.exists(writer['deployed_file']):
                os.remove(writer['deployed_file'])
            if os.path.exists(writer['output_file']):
                os.remove(writer['output_file'])

# ################################################################################################################################

    def test_45_multiple_push_subscribers_all_receive(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 45 - two REST push subscribers and one service push subscriber on one topic
        all receive one injected message.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The second REST receiver, next to the fixture-provided one ..
        second_port = find_free_port()
        second_directory = tempfile.mkdtemp(prefix='zato_test_amqp_bridge_45_')

        second_receiver = WebhookReceiver(second_port, second_directory)
        second_receiver.start()

        # .. and a hot-deployed service that writes to a file.
        writer = _deploy_file_writer_service(zato_dashboard['server_dir'], '45')

        try:
            # Configure the pipeline and all three subscribers via forms ..
            pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '45', _Default_Channel_Service)
            topic_name = pipeline['topic_name']

            _add_rest_push_subscriber(page, base_url, '45a', topic_name, webhook_receiver.port)
            _add_rest_push_subscriber(page, base_url, '45b', topic_name, second_port)
            _add_service_push_subscriber(page, base_url, '45c', topic_name, writer['service_name'])

            # .. inject one message ..
            marker = 'bridge-multi-' + new_cid()
            body = json.dumps({'value': marker})

            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

            # .. and all three subscribers received it.
            first_messages = webhook_receiver.wait_for_delivery(1)
            assert len(first_messages) == 1, f'Expected one delivery for the first receiver, got: {first_messages}'
            assert first_messages[0]['value'] == marker, f'Expected `{marker}`, got: {first_messages[0]}'

            second_messages = second_receiver.wait_for_delivery(1)
            assert len(second_messages) == 1, f'Expected one delivery for the second receiver, got: {second_messages}'
            assert second_messages[0]['value'] == marker, f'Expected `{marker}`, got: {second_messages[0]}'

            lines = _wait_for_file_lines(writer['output_file'], 1)
            assert len(lines) == 1, f'Expected one line from the service subscriber, got: {lines}'
            assert marker in lines[0], f'Expected `{marker}` in `{lines[0]}`'

        finally:
            second_receiver.stop()
            if os.path.exists(writer['deployed_file']):
                os.remove(writer['deployed_file'])
            if os.path.exists(writer['output_file']):
                os.remove(writer['output_file'])

# ################################################################################################################################

    def test_46_fifty_messages_delivered_exactly_once(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 46 - 50 injected messages are delivered exactly once each
        and the queue is fully drained and acked afterwards.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        message_count = 50

        # Configure the pipeline and a REST push subscriber via forms ..
        pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '46', _Default_Channel_Service)
        _add_rest_push_subscriber(page, base_url, '46', pipeline['topic_name'], webhook_receiver.port)

        # .. inject 50 distinct messages ..
        markers = [] # type: list

        for index in range(message_count):
            marker = f'bridge-50-{index}-' + new_cid()
            markers.append(marker)

            body = json.dumps({'value': marker})
            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

        # .. the receiver got all 50, each exactly once ..
        messages = webhook_receiver.wait_for_delivery(message_count, timeout=120)

        received = [item['value'] for item in messages]

        assert len(received) == message_count, f'Expected {message_count} deliveries, got {len(received)}'
        assert sorted(received) == sorted(markers), 'Expected each message exactly once'

        # .. and the queue is empty, everything acked.
        depth = _wait_for_queue_drained(rabbitmq_broker['amqp_url'], pipeline['queue'])
        assert depth == 0, f'Expected an empty queue, got a depth of {depth}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('503', 'Service Unavailable', 'on-amqp-message', 'amqp')
    def test_47_failed_delivery_not_acked_broker_redelivers(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 47 - a failed delivery leaves the message unacked, the broker redelivers
        and after the receiver recovers the message arrives, leaving the queue empty.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the pipeline and a REST push subscriber via forms ..
        pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '47', _Default_Channel_Service)
        _add_rest_push_subscriber(page, base_url, '47', pipeline['topic_name'], webhook_receiver.port)

        # .. the receiver rejects the first delivery and recovers afterwards ..
        webhook_receiver.behavior.set_reject_503(auto_recover_after=1)

        # .. inject one message ..
        marker = 'bridge-redelivery-' + new_cid()
        body = json.dumps({'value': marker})

        publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

        # .. the broker redelivered after the failed attempt and the message finally arrived ..
        messages = webhook_receiver.wait_for_delivery(1, timeout=120)

        assert len(messages) == 1, f'Expected exactly one delivery after redelivery, got: {messages}'
        assert messages[0]['value'] == marker, f'Expected `{marker}`, got: {messages[0]}'

        # .. the first attempt was indeed rejected ..
        assert webhook_receiver.behavior.reject_count == 1, \
            f'Expected one rejection, got {webhook_receiver.behavior.reject_count}'

        # .. and the queue is empty, the redelivered message was acked.
        depth = _wait_for_queue_drained(rabbitmq_broker['amqp_url'], pipeline['queue'])
        assert depth == 0, f'Expected an empty queue, got a depth of {depth}'

# ################################################################################################################################

    def test_48_original_channel_service_suppressed_while_overridden(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 48 - while the override is active, the bridge delivers to subscribers
        and the channel's original service never runs.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The channel's original service writes a marker file when invoked ..
        writer = _deploy_file_writer_service(zato_dashboard['server_dir'], '48')

        try:
            # .. the channel points at the marker service, the topic then overrides it ..
            pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '48', writer['service_name'])
            _add_rest_push_subscriber(page, base_url, '48', pipeline['topic_name'], webhook_receiver.port)

            # .. inject a message ..
            marker = 'bridge-suppressed-' + new_cid()
            body = json.dumps({'value': marker})

            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

            # .. the bridge delivered to the subscriber ..
            messages = webhook_receiver.wait_for_delivery(1)
            assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
            assert messages[0]['value'] == marker, f'Expected `{marker}`, got: {messages[0]}'

            # .. and the marker service never ran.
            assert not os.path.exists(writer['output_file']), \
                f'Expected no marker file, the original service should be suppressed: {writer["output_file"]}'

        finally:
            if os.path.exists(writer['deployed_file']):
                os.remove(writer['deployed_file'])
            if os.path.exists(writer['output_file']):
                os.remove(writer['output_file'])

# ################################################################################################################################

    def test_49_edit_removing_channel_restores_original_service(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 49 - editing the topic to remove its channel restores the channel's
        original service, which then receives injected messages instead of the subscribers.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The channel's original service writes a marker file when invoked ..
        writer = _deploy_file_writer_service(zato_dashboard['server_dir'], '49')

        try:
            # .. the channel points at the marker service, the topic then overrides it ..
            pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '49', writer['service_name'])
            _add_rest_push_subscriber(page, base_url, '49', pipeline['topic_name'], webhook_receiver.port)

            # .. edit the topic via the form to remove the channel ..
            open_edit_dialog(page, 'topic', pipeline['item_id'])

            set_select_value(page, '#id_edit-amqp_channel_name', '')

            submit_edit_form(page)
            time.sleep(_Config_Propagation_Delay)

            # .. inject a message ..
            marker = 'bridge-restored-' + new_cid()
            body = json.dumps({'value': marker})

            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

            # .. the marker service received it ..
            lines = _wait_for_file_lines(writer['output_file'], 1)

            assert len(lines) == 1, f'Expected exactly one line, got: {lines}'
            assert marker in lines[0], f'Expected `{marker}` in `{lines[0]}`'

            # .. and the push subscribers did not.
            assert webhook_receiver.delivered_count() == 0, \
                f'Expected no push deliveries, got {webhook_receiver.delivered_count()}'

        finally:
            if os.path.exists(writer['deployed_file']):
                os.remove(writer['deployed_file'])
            if os.path.exists(writer['output_file']):
                os.remove(writer['output_file'])

# ################################################################################################################################

    def test_50_delete_restores_original_service(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ Item 50 - deleting the AMQP-backed topic restores the channel's original service
        and the topic row is gone from the table.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The channel's original service writes a marker file when invoked ..
        writer = _deploy_file_writer_service(zato_dashboard['server_dir'], '50')

        try:
            # .. the channel points at the marker service, the topic then overrides it ..
            pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '50', writer['service_name'])
            topic_name = pipeline['topic_name']

            # .. delete the topic via the dashboard ..
            trigger_delete(page, 'topic', pipeline['item_id'])
            confirm_delete(page)

            time.sleep(_Config_Propagation_Delay)

            # .. the row is gone ..
            row = find_row_by_name(page, topic_name)
            assert row is None, f'Expected no row for `{topic_name}` after deletion'

            # .. inject a message ..
            marker = 'bridge-deleted-' + new_cid()
            body = json.dumps({'value': marker})

            publish_to_exchange(rabbitmq_broker['amqp_url'], rabbitmq_broker['exchange'], pipeline['binding_key'], body)

            # .. and the marker service received it.
            lines = _wait_for_file_lines(writer['output_file'], 1)

            assert len(lines) == 1, f'Expected exactly one line, got: {lines}'
            assert marker in lines[0], f'Expected `{marker}` in `{lines[0]}`'

        finally:
            if os.path.exists(writer['deployed_file']):
                os.remove(writer['deployed_file'])
            if os.path.exists(writer['output_file']):
                os.remove(writer['output_file'])

# ################################################################################################################################

    def test_51_full_round_trip_publish_to_receiver(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 51 - the complete documented flow, a service calls self.publish, the message
        travels through the outgoing connection to the exchange, the channel consumes it
        and the bridge delivers it to the REST receiver.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the pipeline and a REST push subscriber via forms ..
        pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '51', _Default_Channel_Service)
        topic_name = pipeline['topic_name']

        _add_rest_push_subscriber(page, base_url, '51', topic_name, webhook_receiver.port)

        # .. hot-deploy the publisher service and reach it through a REST channel ..
        publisher = _deploy_publisher_service(zato_dashboard['server_dir'], '51')

        try:
            channel_name = _Test_Name_Prefix + 'channel.rest.51'
            url_path = '/test/amqp/bridge/publisher/' + new_cid()

            create_rest_channel(page, base_url, channel_name, publisher['service_name'], url_path)

            # .. publish through the service ..
            server_port = zato_dashboard['server_port']
            marker = 'bridge-round-trip-' + new_cid()

            response = _post_json(f'http://127.0.0.1:{server_port}{url_path}', {
                'topic_name': topic_name,
                'data': {'value': marker},
            })

            assert response['is_ok'] is True, f'Expected is_ok, got: {response}'

            # .. and the receiver got the message end to end.
            messages = webhook_receiver.wait_for_delivery(1, timeout=60)

            assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
            assert messages[0]['value'] == marker, f'Expected `{marker}`, got: {messages[0]}'

        finally:
            if os.path.exists(publisher['deployed_file']):
                os.remove(publisher['deployed_file'])

# ################################################################################################################################

    def test_52_payload_fidelity_dict_and_string(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ Item 52 - the round trip preserves a JSON dict payload with its types
        and a plain string payload arrives exactly as published.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Configure the pipeline and a REST push subscriber via forms ..
        pipeline = _setup_amqp_pipeline(page, base_url, rabbitmq_broker, '52', _Default_Channel_Service)
        topic_name = pipeline['topic_name']

        _add_rest_push_subscriber(page, base_url, '52', topic_name, webhook_receiver.port)

        # .. hot-deploy the publisher service and reach it through a REST channel ..
        publisher = _deploy_publisher_service(zato_dashboard['server_dir'], '52')

        try:
            channel_name = _Test_Name_Prefix + 'channel.rest.52'
            url_path = '/test/amqp/bridge/fidelity/' + new_cid()

            create_rest_channel(page, base_url, channel_name, publisher['service_name'], url_path)

            server_port = zato_dashboard['server_port']
            channel_url = f'http://127.0.0.1:{server_port}{url_path}'

            # .. a JSON dict payload, with an int and a bool to check type preservation ..
            dict_payload = {'user_id': 123, 'is_active': True, 'name': 'fidelity-' + new_cid()}

            response = _post_json(channel_url, {
                'topic_name': topic_name,
                'data': dict_payload,
            })
            assert response['is_ok'] is True, f'Expected is_ok, got: {response}'

            messages = webhook_receiver.wait_for_delivery(1, timeout=60)
            assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
            assert messages[0] == dict_payload, f'Expected `{dict_payload}`, got: {messages[0]}'

            # .. and a plain string payload ..
            webhook_receiver.clear_output()

            string_payload = 'plain-string-' + new_cid()

            response = _post_json(channel_url, {
                'topic_name': topic_name,
                'data': string_payload,
            })
            assert response['is_ok'] is True, f'Expected is_ok, got: {response}'

            # .. the receiver got it exactly as published, read raw because it is not JSON.
            deadline = time.monotonic() + _File_Wait_Timeout

            raw_messages = _read_receiver_raw(webhook_receiver)

            while time.monotonic() < deadline:
                if raw_messages:
                    break
                time.sleep(0.5)
                raw_messages = _read_receiver_raw(webhook_receiver)

            assert len(raw_messages) == 1, f'Expected exactly one delivery, got: {raw_messages}'
            assert raw_messages[0] == string_payload, f'Expected `{string_payload}`, got `{raw_messages[0]}`'

        finally:
            if os.path.exists(publisher['deployed_file']):
                os.remove(publisher['deployed_file'])

# ################################################################################################################################
# ################################################################################################################################
