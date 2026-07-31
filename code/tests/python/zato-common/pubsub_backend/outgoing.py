# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from threading import RLock
from time import monotonic

# gevent
from gevent import sleep

# Zato
from common import delete_all_rows, get_delivery_rows
from zato.common.api import PubSub
from zato.common.pubsub.outgoing import deliver_envelope, get_outgoing_sub_key, get_outgoing_topic_name, \
    OutgoingPublisher, register_delivery_handler
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.server.base.config_manager import ConfigManager
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_

# ################################################################################################################################
# ################################################################################################################################

# The type of connection this scenario publishes to. It is a type of its own so that what is
# asserted here is the registry doing the choosing rather than any one connection type.
_conn_type = 'file-transfer-test'

# The connections published to, named the way a person names them.
_conn_orders = 'Order Intake'
_conn_archive = 'Archive Upload'

# The connections themselves, by name, the way a server's configuration holds them.
_connections:'anydict' = {}

# How long one wait for an expected outcome may take at most, in seconds -
# generous because a retry sleeps for seconds before its next attempt.
_wait_timeout_seconds = 60

# How long one polling sleep is, in seconds.
_poll_interval_seconds = 0.05

# How many messages the flows that publish more than one of them publish.
_message_count = 5

# How many times the connection in the retry flow refuses a message before accepting it.
_refusal_count = 2

# How quickly the expiring message expires, in seconds.
_short_expiration_seconds = 1

# How long to keep watching for further delivery attempts after a message expired, in seconds.
_quiet_period_seconds = 5

# ################################################################################################################################
# ################################################################################################################################

class _Connection:
    """ Stands in for one outgoing connection - records what reached it and refuses
    as many messages as it was told to refuse.
    """

    def __init__(self) -> 'None':
        self.received:'anylist' = []
        self.attempt_count = 0
        self.refusals_left = 0
        self.refuses_everything = False

# ################################################################################################################################

    def receive(self, data:'str') -> 'None':

        self.attempt_count += 1

        # A connection that is down refuses everything for as long as it is down ..
        if self.refuses_everything:
            raise Exception('The connection is not accepting messages')

        # .. one that is merely busy refuses only its first few messages ..
        if self.refusals_left > 0:
            self.refusals_left -= 1
            raise Exception('The connection refused this message')

        # .. and anything else is accepted.
        self.received.append(data)

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Carries the state that the server's own subscription methods work on. Those methods are
    taken as they are, so what runs here is what runs in a server.
    """

    ensure_outgoing_subscription = ConfigManager.ensure_outgoing_subscription
    restore_outgoing_subscriptions = ConfigManager.restore_outgoing_subscriptions

    def __init__(self, server:'any_') -> 'None':
        self.server = server
        self._push_subs:'anydict' = {}
        self._outgoing_sub_key_cache:'any_' = set()
        self._outgoing_sub_key_lock = RLock()

# ################################################################################################################################
# ################################################################################################################################

class _StubServer:
    """ Stands in for the server - what its invoke does with a message is what the delivery
    service does with it, which is to say it hands the envelope to the registry.
    """

    pubsub_push_delivery: 'PushDelivery'

    def __init__(self, backend:'SQLPubSubBackend') -> 'None':
        self.config_manager = _StubConfigManager(self)
        self.pubsub_backend = backend
        self.invoked:'anylist' = []

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'str') -> 'None':

        self.invoked.append(service_name)

        envelope = loads(payload)
        deliver_envelope(self, 'test-cid', envelope)

# ################################################################################################################################
# ################################################################################################################################

def _deliver_to_test_connection(server:'any_', cid:'str', conn_name:'str', data:'str') -> 'None':
    """ The delivery handler this scenario registers - it finds the connection by the name
    the envelope carried and gives it the message.
    """
    connection = _connections[conn_name]
    connection.receive(data)

# ################################################################################################################################

def _new_connection(conn_name:'str') -> '_Connection':
    """ Puts one connection of the test type in place, replacing whatever an earlier flow left.
    """
    out = _Connection()
    _connections[conn_name] = out

    return out

# ################################################################################################################################

def _new_server() -> 'anytuple':
    """ A backend, a server and the delivery greenlets of one process, which is what a flow
    that models a restart builds a second time.
    """
    backend = SQLPubSubBackend()
    server = _StubServer(backend)
    delivery = PushDelivery(server, backend) # type: ignore[arg-type]

    server.pubsub_push_delivery = delivery

    return backend, server, delivery

# ################################################################################################################################

def _wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls until the condition holds, failing loudly if it does not in time.
    """
    deadline = monotonic() + _wait_timeout_seconds

    while monotonic() < deadline:

        if condition():
            return

        sleep(_poll_interval_seconds)

    raise AssertionError(f'Timed out waiting until {description}')

# ################################################################################################################################
# ################################################################################################################################

def _run_publish_delivers_flow() -> 'None':
    """ One publication reaches the connection it named and leaves that connection's queue empty.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_orders)

    publisher = OutgoingPublisher(server, _conn_type, _conn_orders) # type: ignore[arg-type]
    result = publisher.publish('Order 1234')

    # The publication is a publication like any other, so it has a message id of its own ..
    assert result.msg_id, result

    sub_key = get_outgoing_sub_key(_conn_type, _conn_orders)

    def has_message() -> 'bool':
        out = connection.received == ['Order 1234']
        return out

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # .. the connection receives it ..
    _wait_until(has_message, 'the connection receives the message')

    # .. and it leaves the queue once it has been received ..
    _wait_until(has_empty_queue, 'the message leaves the queue')

    # .. having gone out through the one service every outgoing connection is subscribed by.
    assert server.invoked == [PubSub.Outgoing.Delivery_Service], server.invoked

    delivery.stop()

# ################################################################################################################################

def _run_queue_isolation_flow() -> 'None':
    """ A connection that is down holds up its own queue and nobody else's.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    healthy = _new_connection(_conn_orders)
    down = _new_connection(_conn_archive)
    down.refuses_everything = True

    healthy_publisher = OutgoingPublisher(server, _conn_type, _conn_orders) # type: ignore[arg-type]
    down_publisher = OutgoingPublisher(server, _conn_type, _conn_archive) # type: ignore[arg-type]

    # The connection that is down is published to first, so that it is already retrying
    # while the healthy one is being published to ..
    _ = down_publisher.publish('Archive 1')

    def is_retrying() -> 'bool':
        out = down.attempt_count > 0
        return out

    _wait_until(is_retrying, 'the connection that is down starts retrying')

    for index in range(_message_count):
        _ = healthy_publisher.publish(f'Order {index}')

    def has_everything() -> 'bool':
        count = len(healthy.received)
        out = count == _message_count
        return out

    # .. the healthy connection is delivered to at full speed regardless ..
    _wait_until(has_everything, 'the healthy connection receives everything published to it')

    # .. it received its own messages only ..
    for data in healthy.received:
        assert data.startswith('Order '), healthy.received

    # .. the connection that is down received nothing ..
    assert not down.received, down.received

    # .. its message is still in its queue, which is a queue of its own ..
    down_sub_key = get_outgoing_sub_key(_conn_type, _conn_archive)
    down_rows = get_delivery_rows(down_sub_key)

    assert len(down_rows) == 1, down_rows

    down_topic = get_outgoing_topic_name(_conn_type, _conn_archive)
    first_row = down_rows[0]

    assert first_row.topic_name == down_topic, first_row.topic_name

    # .. and the healthy connection's queue is empty, none of the other one's messages in it.
    healthy_sub_key = get_outgoing_sub_key(_conn_type, _conn_orders)
    healthy_rows = get_delivery_rows(healthy_sub_key)

    assert not healthy_rows, healthy_rows

    delivery.stop()

# ################################################################################################################################

def _run_retry_then_success_flow() -> 'None':
    """ A connection that refuses a message is given it again until it accepts it, once.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_orders)
    connection.refusals_left = _refusal_count

    publisher = OutgoingPublisher(server, _conn_type, _conn_orders) # type: ignore[arg-type]
    _ = publisher.publish('Order 1234')

    def has_message() -> 'bool':
        out = connection.received == ['Order 1234']
        return out

    # The message arrives only after the refusals ran out ..
    _wait_until(has_message, 'the connection accepts the message it kept refusing')

    expected_attempt_count = _refusal_count + 1
    assert connection.attempt_count == expected_attempt_count, connection.attempt_count

    sub_key = get_outgoing_sub_key(_conn_type, _conn_orders)

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # .. and it leaves the queue afterwards, having been accepted exactly once.
    _wait_until(has_empty_queue, 'the message leaves the queue')

    assert connection.received == ['Order 1234'], connection.received

    delivery.stop()

# ################################################################################################################################

def _run_expiration_flow() -> 'None':
    """ A message nobody accepts in time leaves the queue and is not offered again.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(server, _conn_type, _conn_orders) # type: ignore[arg-type]
    _ = publisher.publish('Order 1234', expiration=_short_expiration_seconds)

    sub_key = get_outgoing_sub_key(_conn_type, _conn_orders)

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # The message expires while it is still being retried ..
    _wait_until(has_empty_queue, 'the expired message leaves the queue')

    # .. it was never accepted ..
    assert not connection.received, connection.received

    # .. and the connection is left alone from then on.
    attempt_count_at_expiration = connection.attempt_count
    sleep(_quiet_period_seconds)

    assert connection.attempt_count == attempt_count_at_expiration, connection.attempt_count

    delivery.stop()

# ################################################################################################################################

def _run_restart_recovery_flow() -> 'None':
    """ What a connection's queue holds when a server stops is delivered when it starts again.
    """
    delete_all_rows()

    _, first_server, first_delivery = _new_server()

    connection = _new_connection(_conn_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(first_server, _conn_type, _conn_orders) # type: ignore[arg-type]
    _ = publisher.publish('Order 1234')

    def is_retrying() -> 'bool':
        out = connection.attempt_count > 0
        return out

    _wait_until(is_retrying, 'the message is being retried')

    # The process ends here, and everything its greenlets knew ends with it ..
    first_delivery.stop()

    # .. a server starting up knows nothing of these queues ..
    _, second_server, second_delivery = _new_server()
    assert not second_server.config_manager._push_subs

    # .. and it finds them in the database, one per connection published to before ..
    second_server.config_manager.restore_outgoing_subscriptions()

    sub_key = get_outgoing_sub_key(_conn_type, _conn_orders)
    assert sub_key in second_server.config_manager._push_subs, second_server.config_manager._push_subs

    # .. the connection's name survived the round trip through its own sub key ..
    sub_config_list = second_server.config_manager._push_subs[sub_key]
    sub_config = sub_config_list[0]

    expected_topic = get_outgoing_topic_name(_conn_type, _conn_orders)

    assert sub_config['topic_name'] == expected_topic, sub_config
    assert sub_config['push_type'] == PubSub.Push_Type.Service, sub_config
    assert sub_config['push_service_name'] == PubSub.Outgoing.Delivery_Service, sub_config

    # .. the connection is back up by the time the new greenlets run ..
    connection.refuses_everything = False

    for restored_sub_key in second_server.config_manager._push_subs:
        second_delivery.start_sub_key(restored_sub_key)

    def has_message() -> 'bool':
        out = connection.received == ['Order 1234']
        return out

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # .. and what was left behind is delivered, exactly once.
    _wait_until(has_message, 'the message left behind is delivered after the restart')
    _wait_until(has_empty_queue, 'the message left behind leaves the queue')

    second_delivery.stop()

# ################################################################################################################################

def _run_ordering_flow() -> 'None':
    """ One connection receives its messages in the order they were published in.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_orders)

    publisher = OutgoingPublisher(server, _conn_type, _conn_orders) # type: ignore[arg-type]

    expected:'anylist' = []

    for index in range(_message_count):
        data = f'Order {index}'
        expected.append(data)
        _ = publisher.publish(data)

    def has_everything() -> 'bool':
        count = len(connection.received)
        out = count == _message_count
        return out

    _wait_until(has_everything, 'the connection receives everything published to it')

    assert connection.received == expected, connection.received

    delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def run_outgoing_scenario() -> 'None':
    """ Publishing to an outgoing connection over the shared backend - a publication reaches the
    connection it named, each connection has a queue of its own, a refused message is offered
    again, an expired one is not, what a stopped process left behind is delivered when it starts
    again, and messages arrive in the order they were published in.
    """
    register_delivery_handler(_conn_type, _deliver_to_test_connection)

    _run_publish_delivers_flow()
    _run_queue_isolation_flow()
    _run_retry_then_success_flow()
    _run_expiration_flow()
    _run_restart_recovery_flow()
    _run_ordering_flow()

# ################################################################################################################################
# ################################################################################################################################
