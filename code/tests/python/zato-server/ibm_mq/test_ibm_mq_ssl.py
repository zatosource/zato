# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import channel_config, outgoing_config, run_send_and_consume_scenario, with_ssl
from containers import ModuleCtx as ContainerCtx
from harness import QueueBridgeHarness

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from containers import MQServer

    CertificatePaths = CertificatePaths
    MQServer = MQServer

# ################################################################################################################################
# ################################################################################################################################

def test_ibm_mq_ssl(ibm_mq_ssl_server:'MQServer', certificate_paths:'CertificatePaths') -> 'None':
    """ The send-and-consume scenario over TLS, against a queue manager that requires TLS
    on its channels, plus a negative check that a non-TLS connection is rejected.
    """
    channel = channel_config(
        ibm_mq_ssl_server,
        name='test.ibm-mq.channel',
        queue=ContainerCtx.Request_Queue,
        remove_jms_headers=True,
    )
    channel = with_ssl(channel, certificate_paths)

    publisher = outgoing_config(ibm_mq_ssl_server, name='test.ibm-mq.publisher', queue=ContainerCtx.Request_Queue)
    publisher = with_ssl(publisher, certificate_paths)

    # A second outgoing connection deliberately skips TLS to prove the queue manager rejects it
    plain_publisher = outgoing_config(ibm_mq_ssl_server, name='test.ibm-mq.publisher.plain', queue=ContainerCtx.Request_Queue)

    harness = QueueBridgeHarness()
    harness.start([channel], [publisher, plain_publisher])

    try:
        # The TLS connection can reach its queue ..
        reply = harness.ping('test.ibm-mq.publisher')
        assert reply['status'] == 'ok', f'Ping failed: {reply}'

        # .. a message sent over TLS is consumed by the TLS channel ..
        run_send_and_consume_scenario(harness, 'test.ibm-mq.channel')

        # .. and a connection without TLS is rejected by the TLS-only channel.
        reply = harness.ping('test.ibm-mq.publisher.plain')
        assert reply['status'] == 'error', f'Expected the non-TLS ping to fail: {reply}'

    finally:
        harness.stop()

# ################################################################################################################################
# ################################################################################################################################
