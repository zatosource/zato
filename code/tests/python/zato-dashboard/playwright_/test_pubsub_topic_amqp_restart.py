# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import subprocess
import tempfile
import time
from http.client import OK
from urllib.request import Request, urlopen

# kombu
from kombu import Connection

# pytest
import pytest

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.playwright_pubsub import create_amqp_channel, create_amqp_topic, create_basic_auth, \
    create_outgoing_amqp, create_outgoing_rest_with_address, create_permission, create_push_rest_subscription, \
    get_item_id, navigate_to_page, open_publish_overlay, publish_via_overlay
from zato.common.test.rabbitmq_ import declare_and_bind, drain_queue, publish_to_exchange
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.process_util import kill_process_tree
from zato.common.util.api import new_cid

# The broker fixture is resolved by pytest through this import
from amqp_fixtures import rabbitmq_broker # noqa: F401

# The conftest's atexit cleanup reads this dict, so handing the new process over here means it will be killed at exit
from cleanup_refs import cleanup_refs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

_Topic_Page_Url = '/zato/pubsub/topic/?cluster=1'

_Test_Name_Prefix = 'test.amqp.restart.' + new_cid() + '.'

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# The service AMQP channels invoke when the tests do not care about the target
_Default_Channel_Service = 'demo.ping'

# How long the config event needs to reach the runtime registry after a form submission
_Config_Propagation_Delay = 1.0

# How long to wait for the restarted server to answer pings
_Restart_Timeout = 180

# How long to wait for the channel's consumer to attach to its queue
_Consumer_Wait_Timeout = 60

# State shared between the restart tests - the registry test configures and restarts,
# the override test verifies the inbound side of the same, already restarted server
_shared_state = {} # type: dict

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

def _read_process_environment(pid:'int') -> 'dict':
    """ Reads the environment of a running process so the restarted one gets the same variables,
    including the dynamic ports the fixture chose at startup.
    """
    with open(f'/proc/{pid}/environ', 'rb') as environ_file:
        raw = environ_file.read()

    out = {} # type: dict

    for entry in raw.decode('utf8', errors='replace').split('\0'):
        if '=' in entry:
            key, _, value = entry.partition('=')
            out[key] = value

    return out

# ################################################################################################################################

def _restart_server(zato_dashboard:'anydict') -> 'None':
    """ Stops the server subprocess and starts a new one with the same environment,
    then waits until it answers pings again.
    """
    server_process = zato_dashboard['server_process']
    server_dir = zato_dashboard['server_dir']
    server_port = zato_dashboard['server_port']
    host = zato_dashboard['host']

    # Capture the environment before the process goes away ..
    server_environment = _read_process_environment(server_process.pid)

    # .. stop the server along with its whole process group - terminating just
    # the launcher would leave the actual server running and holding the port ..
    kill_process_tree(server_process)

    # .. start a new one with the same environment ..
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    new_process = subprocess.Popen(
        [zato_bin, 'start', server_dir, '--fg'],
        env=server_environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    # .. hand the new process over to the conftest so its cleanup kills it at exit ..
    zato_dashboard['server_process'] = new_process
    cleanup_refs['server_process'] = new_process

    # .. and wait until the server answers pings again.
    # .. The browser is intentionally idle during this wait, the server is restarting ..
    logger.info('The server was stopped on purpose, waiting up to %ss for it to come back after the restart', _Restart_Timeout)

    url = f'http://{host}:{server_port}/zato/ping'
    deadline = time.monotonic() + _Restart_Timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == OK:
                    return
        except Exception:
            time.sleep(1)

    raise RuntimeError(f'The server did not come back within {_Restart_Timeout}s after the restart')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def module_receiver() -> 'WebhookReceiver':
    """ A module-scoped local HTTP receiver so it survives across the restart tests.
    """
    receiver_port = find_free_port()
    output_directory = tempfile.mkdtemp(prefix='zato_test_amqp_restart_')

    receiver = WebhookReceiver(receiver_port, output_directory)
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicAMQPRestart:
    """ Restart tests - the registry and the channel override are rebuilt from the ODB
    at startup, without any config events since.
    """

    def test_restart_rebuilds_registry(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        module_receiver:'WebhookReceiver',
        ) -> 'None':
        """ After a server restart, with no config events fired since startup,
        a publish through the overlay still routes to AMQP, proving _sync_pubsub_topics
        rebuilt the registry from opaque1.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        address = _get_broker_address(rabbitmq_broker)

        # A dedicated queue for the channel, next to the fixture-provided one ..
        unique = new_cid()
        channel_queue = 'restart.queue.' + unique
        channel_binding_key = 'restart.key.' + unique

        declare_and_bind(amqp_url, exchange, channel_queue, channel_binding_key)

        # .. configure everything via forms before the restart ..

        # .. the outgoing connection ..
        outconn_name = _Test_Name_Prefix + 'outconn.53'
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. the AMQP channel ..
        channel_name = _Test_Name_Prefix + 'channel.53'
        _ = create_amqp_channel(
            page, base_url, channel_name, address, _Broker_Username, _Broker_Password,
            channel_queue, _Default_Channel_Service)

        # .. the topic - its publishes go to the fixture queue, its channel consumes the dedicated one ..
        topic_name = _Test_Name_Prefix + 'topic.53'
        _ = create_amqp_topic(
            page, base_url, topic_name, outconn_name, exchange, rabbitmq_broker['routing_key'], channel_name)

        # .. a REST push subscriber for the inbound side, verified by the override test ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'restart')
        _ = create_permission(page, base_url, sec_info['name'], 'subscriber', 'sub', topic_name)

        rest_name = _Test_Name_Prefix + 'rest.53'
        create_outgoing_rest_with_address(page, base_url, rest_name, f'http://127.0.0.1:{module_receiver.port}', '/push')
        create_push_rest_subscription(page, base_url, sec_info['name'], topic_name, rest_name)

        time.sleep(_Config_Propagation_Delay)

        # .. drain anything left on the fixture queue ..
        _ = drain_queue(amqp_url, rabbitmq_broker['queue'], timeout=1)

        # .. restart the server - everything from here on runs on registry state
        # .. rebuilt from the ODB, with no config events fired since startup ..
        _restart_server(zato_dashboard)

        # .. share the setup with the override test ..
        _shared_state['topic_name'] = topic_name
        _shared_state['channel_queue'] = channel_queue
        _shared_state['channel_binding_key'] = channel_binding_key

        # .. reload the topics page after the restart and find the topic's row id again ..
        navigate_to_page(page, base_url, _Topic_Page_Url)
        item_id = get_item_id(page, topic_name)

        # .. publish through the overlay ..
        payload = 'restart-payload-' + new_cid()

        open_publish_overlay(page, item_id)
        publish_via_overlay(page, payload)

        # .. and the message landed on the RabbitMQ queue.
        messages = drain_queue(amqp_url, rabbitmq_broker['queue'])

        assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
        assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################

    def test_restart_reapplies_override(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        module_receiver:'WebhookReceiver',
        ) -> 'None':
        """ After the restart, an injected message still reaches the REST receiver
        through the bridge, proving the channel override was reapplied by the startup sync.
        """
        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']

        # The setup and the restart happened in the registry test ..
        channel_binding_key = _shared_state['channel_binding_key']
        channel_queue = _shared_state['channel_queue']

        # .. make sure the restarted channel's consumer is attached ..
        _wait_for_consumer(amqp_url, channel_queue)

        # .. inject a message the way an external AMQP producer would ..
        marker = 'restart-bridge-' + new_cid()
        body = json.dumps({'value': marker})

        publish_to_exchange(amqp_url, exchange, channel_binding_key, body)

        # .. and the receiver got it through the bridge.
        messages = module_receiver.wait_for_delivery(1)

        assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
        assert messages[0]['value'] == marker, f'Expected `{marker}`, got: {messages[0]}'

# ################################################################################################################################
# ################################################################################################################################
