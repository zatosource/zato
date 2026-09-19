# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What is particular to a queue whose topic is AMQP-backed.

# pytest
import pytest

# kombu
from kombu import Connection

# Zato
from zato.common.test.rabbitmq_ import RabbitMQProcess
from zato.common.typing_ import cast_

# Test support
from _helpers import Connections, get_client, get_queue, get_receiver, is_broker_backend, send, TestConfig, \
    wait_for_queue_depth

# ################################################################################################################################
# ################################################################################################################################

_queue_conn = Connections['orders']

_not_a_broker_reason = 'The queues of this backend are in the pub/sub database'
_not_tls_reason = 'This broker is not a TLS-only one'

_plain_connect_timeout = 2
_plain_connect_retries = 1

# ################################################################################################################################
# ################################################################################################################################

def test_a_waiting_message_is_in_the_broker_and_not_in_the_pubsub_database() -> 'None':
    """ A message the endpoint turned down waits in the broker's queue.
    """
    if not is_broker_backend():
        pytest.skip(_not_a_broker_reason)

    client = get_client()
    receiver = get_receiver('orders')

    receiver.refuse_all()

    result = send(client, _queue_conn, {'order_id': 'in-the-broker'})

    assert result['is_in_queue'] is True
    assert result['msg_id']

    queue = get_queue(client, _queue_conn)
    assert queue['depth'] == 1

    assert queue['messages'] == []

    receiver.accept_all()

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    queue = wait_for_queue_depth(client, _queue_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_a_tls_only_broker_refuses_a_plain_connection() -> 'None':
    """ The TLS backend's broker accepts no plain AMQP connection.
    """
    if not is_broker_backend():
        pytest.skip(_not_a_broker_reason)

    broker = cast_(RabbitMQProcess, TestConfig.backend.broker)

    if not broker.needs_ssl:
        pytest.skip(_not_tls_reason)

    plain_url = broker.amqp_url.replace('amqps://', 'amqp://')

    try:
        with Connection(plain_url) as connection:
            _ = connection.ensure_connection(max_retries=_plain_connect_retries, timeout=_plain_connect_timeout)

    except Exception:
        connected = False

    else:
        connected = True

    assert not connected, 'A plain AMQP connection to a TLS-only broker unexpectedly succeeded'

# ################################################################################################################################
# ################################################################################################################################
