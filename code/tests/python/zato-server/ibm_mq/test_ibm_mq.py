# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import channel_config, outgoing_config, run_reply_scenario, run_rfh2_scenario, run_send_and_consume_scenario
from containers import ModuleCtx as ContainerCtx
from harness import ModuleCtx as HarnessCtx, QueueBridgeHarness
from mq_client import MQTestClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import MQServer
    MQServer = MQServer

# ################################################################################################################################
# ################################################################################################################################

def test_ibm_mq(ibm_mq_server:'MQServer') -> 'None':
    """ The complete IBM MQ scenario against a live queue manager - ping, an outgoing send consumed
    by a channel with MQMD headers, a reply-to round trip and MQRFH2 messages with header removal on and off.
    """

    # One channel strips MQRFH2 headers, the other keeps them in the payload
    channels = [
        channel_config(ibm_mq_server, name='test.ibm-mq.channel', queue=ContainerCtx.Request_Queue, remove_jms_headers=True),
        channel_config(
            ibm_mq_server,
            name='test.ibm-mq.channel.keep-headers',
            queue=ContainerCtx.Keep_Headers_Queue,
            remove_jms_headers=False,
        ),
    ]

    outgoing = [
        outgoing_config(ibm_mq_server, name='test.ibm-mq.publisher', queue=ContainerCtx.Request_Queue),
    ]

    harness = QueueBridgeHarness()
    harness.start(channels, outgoing)

    client = MQTestClient(
        HarnessCtx.MQ_Client_Lib,
        ibm_mq_server.address,
        ContainerCtx.MQ_Channel_Name,
        ContainerCtx.Queue_Manager,
        ContainerCtx.Username,
        ContainerCtx.Password,
    )
    client.connect()

    try:
        # The outgoing connection can reach its queue ..
        reply = harness.ping('test.ibm-mq.publisher')
        assert reply['status'] == 'ok', f'Ping failed: {reply}'

        # .. an outgoing send is consumed by the channel ..
        run_send_and_consume_scenario(harness, 'test.ibm-mq.channel')

        # .. a request with a reply-to queue receives a correlated reply ..
        run_reply_scenario(harness, client, 'test.ibm-mq.channel')

        # .. MQRFH2 headers are stripped from the payload when the channel says so ..
        run_rfh2_scenario(harness, client, queue=ContainerCtx.Request_Queue, remove_jms_headers=True)

        # .. and kept in the payload when it does not.
        run_rfh2_scenario(harness, client, queue=ContainerCtx.Keep_Headers_Queue, remove_jms_headers=False)

    finally:
        client.disconnect()
        harness.stop()

# ################################################################################################################################
# ################################################################################################################################
