# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import time

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from live_kafka.containers import create_topic, start_kafka, stop_container
from kafka_channel import create_kafka_channel, delete_kafka_channel
from kafka_outconn import create_kafka_outconn, delete_kafka_outconn
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.kafka.live.' + CryptoManager.generate_hex_string(32) + '.'

# The pre-deployed fixture services this suite drives and routes to
_Invoker_Service  = 'test.kafka.invoke'
_Receiver_Service = 'test.kafka.receiver'

# Where the queue bridge binary lives
_Repo_Dir = os.environ['ZATO_TEST_BASE_DIR']
_Bridge_Binary = os.path.join(_Repo_Dir, 'code', 'bin', '_zato_queue_bridge')

# How long to keep retrying an invocation while a UI change propagates to the server and the bridge
_Propagation_Timeout = 120

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def kafka_server() -> 'any_':
    """ A module-scoped live Kafka broker in Docker.
    """
    server = start_kafka()

    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='module')
def queue_bridge(kafka_server:'any_', zato_dashboard:'anydict') -> 'any_':
    """ The queue bridge binary running as a subprocess against the test session's
    dedicated Redis, the same way the server runs it in production. The server under
    test talks to it through the shared Redis streams - dedicated because servers
    left over from other test sessions in the same run read the default Redis
    and would steal recv events from the shared consumer groups.
    """
    env = os.environ.copy()
    env['Zato_Queue_Bridge_Redis_Port'] = str(zato_dashboard['queue_bridge_redis_port'])

    process = subprocess.Popen([_Bridge_Binary], env=env)

    yield process

    process.terminate()
    _ = process.wait(timeout=10)

# ################################################################################################################################
# ################################################################################################################################

def _open_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed Kafka invoker service in the IDE and waits until the Invoke button is usable.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{_Invoker_Service}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

# ################################################################################################################################

def _wait_for_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness
    probe until the service responds, confirming it deployed during server boot.
    """

    _open_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            last_error = probe_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            if response.get('is_ready'):
                return
            time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'Service `{_Invoker_Service}` did not deploy within {_Propagation_Timeout}s, last: {last_error!r}')

# ################################################################################################################################

def _send_with_retry(page:'Page', base_url:'str', connection_name:'str', payload:'str') -> 'None':
    """ Sends one message through the pre-deployed service, driven from the IDE in the browser,
    retrying while the connection configured a moment ago propagates to the server and the bridge.
    """

    _open_invoker_in_ide(page, base_url)

    request = {
        'mode': 'send',
        'connection': connection_name,
        'payload': payload,
    }

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_service_in_ide(page, request)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            # The service reports errors as a reply field, e.g. while the connection
            # configured a moment ago is still propagating.
            if error := out.get('error'):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return

    raise Exception(f'Could not send over `{connection_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################

def _wait_for_received(page:'Page', base_url:'str', marker:'str') -> 'anydict':
    """ Polls the receiver service until a message with the given marker arrives and returns it.
    """

    _open_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Propagation_Timeout

    while time.monotonic() < deadline:
        response = invoke_service_in_ide(page, {'mode': 'get-received'})

        for message in response['received']:
            if marker in message['input']:
                return message

        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'No message with marker `{marker}` arrived within {_Propagation_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestKafkaEndToEnd:
    """ The live end-to-end flow - a Kafka channel and an outgoing connection, both created
    through the Dashboard against a broker in Docker, with the queue bridge binary running
    the way it does in production. One send from a service goes through the outgoing
    connection to the topic, the channel consumes it and the receiver service records it
    through both self.request.input and self.request.raw_request.
    """

# ################################################################################################################################

    def test_end_to_end_send_and_consume(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        kafka_server:'any_',
        queue_bridge:'any_',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _wait_for_invoker_service(page, base_url)
        _ = invoke_service_in_ide(page, {'mode': 'clear-received'})

        # The channel and the outgoing connection need distinct names because
        # the dashboard's uniqueness check spans all generic connections.
        channel_name = _Test_Name_Prefix + 'channel'
        outconn_name = _Test_Name_Prefix + 'outconn'
        topic_name   = _Test_Name_Prefix + 'topic'
        group_id     = _Test_Name_Prefix + 'group'

        # The topic exists before the channel subscribes to it - consumers only discover
        # topics created after subscription on their next metadata refresh, minutes later.
        create_topic(kafka_server.container_name, topic_name)

        # The channel - it consumes from the topic and routes to the receiver service ..
        channel_id = create_kafka_channel(page, base_url, channel_name, {
            'address': kafka_server.address,
            'topic': topic_name,
            'group_id': group_id,
            'service': _Receiver_Service,
        })

        # .. and the outgoing connection pointed at the same topic.
        outconn_id = create_kafka_outconn(page, base_url, outconn_name, {
            'address': kafka_server.address,
            'topic': topic_name,
        })

        # One send now goes service -> outgoing connection -> topic -> channel -> receiver service.
        marker = CryptoManager.generate_hex_string()
        payload = json.dumps({'marker': marker, 'source': 'dashboard-end-to-end'})
        _send_with_retry(page, base_url, outconn_name, payload)

        # The receiver recorded the message through both request attributes.
        message = _wait_for_received(page, base_url, marker)

        assert json.loads(message['input']) == {'marker': marker, 'source': 'dashboard-end-to-end'}
        assert message['raw_request'] == message['input']

        # Clean up.
        delete_kafka_outconn(page, outconn_id)
        delete_kafka_channel(page, channel_id)

# ################################################################################################################################
# ################################################################################################################################
