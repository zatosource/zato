# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys
import time

# The IBM MQ container and ctypes client helpers live in the queue bridge live test suite
_mq_helpers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-server', 'ibm_mq'))
if _mq_helpers_dir not in sys.path:
    sys.path.insert(0, _mq_helpers_dir)

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from containers import ModuleCtx as ContainerCtx, start_ibm_mq, stop_container
from ibm_mq_channel import change_ibm_mq_channel_password, create_ibm_mq_channel, delete_ibm_mq_channel
from ibm_mq_outconn import change_ibm_mq_outconn_password, create_ibm_mq_outconn, delete_ibm_mq_outconn
from mq_client import MQTestClient, ModuleCtx as MQClientCtx
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.ibm-mq.live.' + CryptoManager.generate_hex_string(32) + '.'

# The pre-deployed fixture services this suite drives and routes to
_Invoker_Service  = 'test.ibm-mq.invoke'
_Receiver_Service = 'test.ibm-mq.receiver'

# Where the queue bridge binary and the MQ client library live
_Repo_Dir = os.environ['ZATO_TEST_BASE_DIR']
_Bridge_Binary = os.path.join(_Repo_Dir, 'code', 'bin', '_zato_queue_bridge')
_MQ_Client_Lib = os.path.join(_Repo_Dir, 'lib', 'mqm', 'lib64', 'libmqm_r.so')

# How long to keep retrying an invocation while a UI change propagates to the server and the bridge
_Propagation_Timeout = 120

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# How long to wait for the reply put on the reply-to queue
_Reply_Wait_Ms = 30000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def ibm_mq_server() -> 'any_':
    """ A module-scoped live IBM MQ queue manager in Docker.
    """
    server = start_ibm_mq(needs_ssl=False)

    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='module')
def queue_bridge(ibm_mq_server:'any_') -> 'any_':
    """ The queue bridge binary running as a subprocess against the local Redis,
    the same way the server runs it in production. The server under test talks
    to it through the shared Redis streams.
    """
    env = os.environ.copy()
    env['Zato_MQ_Client_Lib'] = _MQ_Client_Lib

    process = subprocess.Popen([_Bridge_Binary], env=env)

    yield process

    process.terminate()
    _ = process.wait(timeout=10)

# ################################################################################################################################
# ################################################################################################################################

def _open_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed IBM MQ invoker service in the IDE and waits until the Invoke button is usable.
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
            if marker in message['data']:
                return message

        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'No message with marker `{marker}` arrived within {_Propagation_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestIBMMQEndToEnd:
    """ The live end-to-end flow - an IBM MQ channel and an outgoing connection, both created
    through the Dashboard against a queue manager in Docker, with the queue bridge binary
    running the way it does in production. One send from a service goes through the outgoing
    connection to the queue, the channel consumes it and the receiver service records it,
    then a request with a reply-to queue proves the automatic reply path.
    """

# ################################################################################################################################

    def test_end_to_end_send_consume_and_reply(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ibm_mq_server:'any_',
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

        # The channel - it consumes from the request queue and routes to the receiver service ..
        channel_id = create_ibm_mq_channel(page, base_url, channel_name, {
            'address': ibm_mq_server.address,
            'queue_manager': ContainerCtx.Queue_Manager,
            'mq_channel_name': ContainerCtx.MQ_Channel_Name,
            'queue': ContainerCtx.Request_Queue,
            'service': _Receiver_Service,
            'username': ContainerCtx.Username,
            'remove_jms_headers': True,
        })
        change_ibm_mq_channel_password(page, channel_id, ContainerCtx.Password)

        # .. and the outgoing connection pointed at the same queue.
        outconn_id = create_ibm_mq_outconn(page, base_url, outconn_name, {
            'address': ibm_mq_server.address,
            'queue_manager': ContainerCtx.Queue_Manager,
            'mq_channel_name': ContainerCtx.MQ_Channel_Name,
            'queue': ContainerCtx.Request_Queue,
            'username': ContainerCtx.Username,
        })
        change_ibm_mq_outconn_password(page, outconn_id, ContainerCtx.Password)

        # One send now goes service -> outgoing connection -> queue -> channel -> receiver service.
        marker = CryptoManager.generate_hex_string()
        payload = json.dumps({'marker': marker, 'source': 'dashboard-e2e'})
        _send_with_retry(page, base_url, outconn_name, payload)

        # The receiver recorded the message together with its MQMD headers.
        message = _wait_for_received(page, base_url, marker)

        assert json.loads(message['data']) == {'marker': marker, 'source': 'dashboard-e2e'}
        assert message['headers']['mqmd.format'] == 'MQSTR'
        assert len(message['headers']['mqmd.message_id']) == 48

        # Now the automatic reply - a request naming a reply-to queue goes onto the channel's queue
        # and the receiver's response payload comes back correlated with the request's message ID.
        client = MQTestClient(
            library_path=_MQ_Client_Lib,
            address=ibm_mq_server.address,
            mq_channel_name=ContainerCtx.MQ_Channel_Name,
            queue_manager=ContainerCtx.Queue_Manager,
            username=ContainerCtx.Username,
            password=ContainerCtx.Password,
        )
        client.connect()

        try:
            reply_marker = CryptoManager.generate_hex_string()
            request_data = json.dumps({'marker': reply_marker}).encode('utf-8')

            request_message_id = client.put(
                ContainerCtx.Request_Queue,
                request_data,
                message_type=MQClientCtx.MQMT_Request,
                reply_to_queue=ContainerCtx.Reply_Queue,
                reply_to_queue_manager=ContainerCtx.Queue_Manager,
            )

            received = client.get(ContainerCtx.Reply_Queue, wait_ms=_Reply_Wait_Ms, correlation_id=request_message_id)
            assert received is not None, 'No reply arrived on the reply-to queue'

            reply_payload, reply_fields = received
            assert json.loads(reply_payload) == {'received': request_data.decode('utf-8')}
            assert reply_fields['correlation_id'] == request_message_id

        finally:
            client.disconnect()

        # Clean up.
        delete_ibm_mq_outconn(page, outconn_id)
        delete_ibm_mq_channel(page, channel_id)

# ################################################################################################################################
# ################################################################################################################################
