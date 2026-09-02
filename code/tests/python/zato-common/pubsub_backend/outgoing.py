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
from common import delete_all_rows, get_delivery_rows, get_message_rows, get_sub_rows, move_message_rows
from zato.common.api import PubSub
from zato.common.pubsub.outgoing import deliver_envelope, get_outgoing_sub_key, get_outgoing_topic_name, \
    OutgoingPublisher, register_outgoing_conn_type
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.typing_ import cast_
from zato.server.base.config_manager import ConfigManager
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The type of connection this scenario publishes to. It is a type of its own so that what is
# asserted here is the registry doing the choosing rather than any one connection type.
_conn_type = 'file-transfer-test'

# A second type, for the flow that has two of them sharing one connection name
_other_conn_type = 'sdk-transfer-test'

# The connections published to, by the id each of them keeps for as long as it exists.
_conn_id_orders = 17
_conn_id_archive = 23

# The names those connections go by, the way a person names them, and the one a rename gives.
_name_orders = 'Order Intake'
_name_archive = 'Archive Upload'
_name_orders_renamed = 'Order Intake EU'

# The connections themselves, by id, the way a server's configuration holds them. Each type has
# its own set, because a name and an id mean something only within one type of connection.
_connections:'anydict' = {}
_other_connections:'anydict' = {}

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

# How long the connection in the rename-during-delivery flow holds on to a message, in seconds.
_hold_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

class _Connection:
    """ Stands in for one outgoing connection - records what reached it, goes by a name that a rename
    changes and an id that it does not, and refuses as many messages as it was told to refuse.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self.received:'anylist' = []
        self.attempt_count = 0
        self.refusals_left = 0
        self.refuses_everything = False
        self.hold_seconds = 0
        self.is_receiving = False

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

        # .. one that is slow keeps the delivery for a while, which is what a rename has to wait for ..
        if self.hold_seconds:
            self.is_receiving = True
            sleep(self.hold_seconds)
            self.is_receiving = False

        # .. and anything else is accepted.
        self.received.append(data)

# ################################################################################################################################
# ################################################################################################################################

class _StubConfigManager:
    """ Carries the state that the server's own subscription methods work on. Those methods are
    taken as they are, so what runs here is what runs in a server.
    """

    get_outgoing_publish_lock = ConfigManager.get_outgoing_publish_lock
    _set_outgoing_topic_audit_flag = ConfigManager._set_outgoing_topic_audit_flag
    ensure_outgoing_subscription = ConfigManager.ensure_outgoing_subscription
    rename_outgoing_subscription = ConfigManager.rename_outgoing_subscription
    delete_outgoing_subscription = ConfigManager.delete_outgoing_subscription
    restore_outgoing_subscriptions = ConfigManager.restore_outgoing_subscriptions

    def __init__(self, server:'any_') -> 'None':
        self.server = server
        self._push_subs:'anydict' = {}
        self._outgoing_sub_key_cache:'any_' = set()
        self._outgoing_sub_key_lock = RLock()
        self._outgoing_conn_locks:'anydict' = {}

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
        deliver_envelope(_as_server(self), 'test-cid', envelope)

# ################################################################################################################################
# ################################################################################################################################

def _as_server(server:'_StubServer') -> 'ParallelServer':
    """ The stub in the shape that the code being tested is typed for.
    """
    out = cast_('ParallelServer', server)
    return out

# ################################################################################################################################

def _locate_test_connection(server:'any_', conn_id:'int') -> 'anytuple':
    """ The locator this scenario registers - it finds a connection by the id it is published to under,
    which is the id it keeps through a rename, and answers with the name it goes by now.
    """
    connection = _connections.get(conn_id)

    if not connection:
        return ()

    out = (connection.name, connection)
    return out

# ################################################################################################################################

def _locate_other_test_connection(server:'any_', conn_id:'int') -> 'anytuple':
    """ The locator of the second type - it looks in that type's own set of connections, which is
    what keeps an id or a name from meaning anything outside the type it belongs to.
    """
    connection = _other_connections.get(conn_id)

    if not connection:
        return ()

    out = (connection.name, connection)
    return out

# ################################################################################################################################

def _deliver_to_test_connection(server:'any_', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ The delivery handler this scenario registers - it gives the message to what the locator found.
    """
    wrapper.receive(data)

# ################################################################################################################################

def _new_connection(conn_id:'int', name:'str') -> '_Connection':
    """ Puts one connection of the test type in place, replacing whatever an earlier flow left.
    """
    out = _Connection(name)
    _connections[conn_id] = out

    return out

# ################################################################################################################################

def _new_other_connection(conn_id:'int', name:'str') -> '_Connection':
    """ The same, for the second type of connection.
    """
    out = _Connection(name)
    _other_connections[conn_id] = out

    return out

# ################################################################################################################################

def _rename_connection(server:'_StubServer', conn_id:'int', new_name:'str') -> 'None':
    """ Renames a connection the way a config event does - the configuration says the new name first,
    and the topic follows it, both under the lock that publications to the connection take.
    """
    connection = _connections[conn_id]
    old_name = connection.name

    config_manager = server.config_manager

    with config_manager.get_outgoing_publish_lock(_conn_type, conn_id):
        connection.name = new_name
        config_manager.rename_outgoing_subscription(_conn_type, conn_id, old_name, new_name)

# ################################################################################################################################

def _delete_connection(server:'_StubServer', conn_id:'int') -> 'None':
    """ Deletes a connection the way a config event does - the connection goes first and its queue with it.
    """
    connection = _connections.pop(conn_id)
    server.config_manager.delete_outgoing_subscription(_conn_type, conn_id, connection.name)

# ################################################################################################################################

def _new_server() -> 'anytuple':
    """ A backend, a server and the delivery greenlets of one process, which is what a flow
    that models a restart builds a second time.
    """
    backend = SQLPubSubBackend()
    server = _StubServer(backend)
    delivery = PushDelivery(_as_server(server), backend)

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
    connection = _new_connection(_conn_id_orders, _name_orders)

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    result = publisher.publish('Order 1234')

    # The publication is a publication like any other, so it has a message id of its own ..
    assert result.msg_id, result

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)

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

    healthy = _new_connection(_conn_id_orders, _name_orders)
    down = _new_connection(_conn_id_archive, _name_archive)
    down.refuses_everything = True

    healthy_publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    down_publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_archive)

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
    down_sub_key = get_outgoing_sub_key(_conn_type, _conn_id_archive)
    down_rows = get_delivery_rows(down_sub_key)

    assert len(down_rows) == 1, down_rows

    down_topic = get_outgoing_topic_name(_conn_type, _name_archive)
    first_row = down_rows[0]

    assert first_row.topic_name == down_topic, first_row.topic_name

    # .. and the healthy connection's queue is empty, none of the other one's messages in it.
    healthy_sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    healthy_rows = get_delivery_rows(healthy_sub_key)

    assert not healthy_rows, healthy_rows

    delivery.stop()

# ################################################################################################################################

def _run_retry_then_success_flow() -> 'None':
    """ A connection that refuses a message is given it again until it accepts it, once.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refusals_left = _refusal_count

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order 1234')

    def has_message() -> 'bool':
        out = connection.received == ['Order 1234']
        return out

    # The message arrives only after the refusals ran out ..
    _wait_until(has_message, 'the connection accepts the message it kept refusing')

    expected_attempt_count = _refusal_count + 1
    assert connection.attempt_count == expected_attempt_count, connection.attempt_count

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)

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

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order 1234', expiration=_short_expiration_seconds)

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)

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

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(first_server), _conn_type, _conn_id_orders)
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

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    assert sub_key in second_server.config_manager._push_subs, second_server.config_manager._push_subs

    # .. the connection its queue belongs to was found by the id that sub key carries ..
    sub_config_list = second_server.config_manager._push_subs[sub_key]
    sub_config = sub_config_list[0]

    expected_topic = get_outgoing_topic_name(_conn_type, _name_orders)

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
    connection = _new_connection(_conn_id_orders, _name_orders)

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)

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

def _run_rename_flow() -> 'None':
    """ A message queued before a connection is renamed is delivered to that connection afterwards.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order 1234')

    def is_retrying() -> 'bool':
        out = connection.attempt_count > 0
        return out

    # The message is in the queue of a connection that is not taking anything ..
    _wait_until(is_retrying, 'the message is being retried')

    # .. the connection is renamed while that message is still queued ..
    _rename_connection(server, _conn_id_orders, _name_orders_renamed)

    # .. and it comes back up under its new name ..
    connection.refuses_everything = False

    def has_message() -> 'bool':
        out = connection.received == ['Order 1234']
        return out

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # .. the message queued before the rename is delivered after it, exactly once ..
    _wait_until(has_message, 'the message queued before the rename is delivered')
    _wait_until(has_empty_queue, 'the message leaves the queue')

    assert connection.received == ['Order 1234'], connection.received

    # .. through the queue it was always in, of which there is one ..
    outgoing_sub_keys = server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
    assert outgoing_sub_keys == [sub_key], outgoing_sub_keys

    # .. under the topic of the new name ..
    new_topic = get_outgoing_topic_name(_conn_type, _name_orders_renamed)
    sub_rows = get_sub_rows(sub_key)

    assert len(sub_rows) == 1, sub_rows
    assert sub_rows[0].topic_name == new_topic, sub_rows[0].topic_name

    # .. and nothing at all is left under the old one.
    old_topic = get_outgoing_topic_name(_conn_type, _name_orders)
    old_messages = get_message_rows(old_topic)

    assert not old_messages, old_messages

    delivery.stop()

# ################################################################################################################################

def _run_rename_during_delivery_flow() -> 'None':
    """ A rename waits for the delivery that is already under way, so that message is not handed over twice.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.hold_seconds = _hold_seconds

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order 1234')

    def is_receiving() -> 'bool':
        out = connection.is_receiving
        return out

    # The connection has the message in its hands and is not done with it ..
    _wait_until(is_receiving, 'the connection is in the middle of receiving the message')

    # .. the rename runs into exactly that ..
    _rename_connection(server, _conn_id_orders, _name_orders_renamed)

    # .. and by the time it is over, that delivery has finished ..
    assert not connection.is_receiving, connection.is_receiving
    assert connection.received == ['Order 1234'], connection.received

    # .. it was acknowledged too, so nothing is left to be handed over a second time ..
    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    rows = get_delivery_rows(sub_key)

    assert not rows, rows

    # .. and the connection is not given the message again.
    sleep(_quiet_period_seconds)

    assert connection.received == ['Order 1234'], connection.received
    assert connection.attempt_count == 1, connection.attempt_count

    delivery.stop()

# ################################################################################################################################

def _run_rename_one_queue_flow() -> 'None':
    """ A renamed connection has the one queue it always had, not a second one next to it.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order before')

    def has_first_message() -> 'bool':
        out = connection.received == ['Order before']
        return out

    _wait_until(has_first_message, 'the connection receives what was published before the rename')

    sub_key_before = get_outgoing_sub_key(_conn_type, _conn_id_orders)

    _rename_connection(server, _conn_id_orders, _name_orders_renamed)

    # The queue is the same one as before the rename ..
    sub_key_after = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    assert sub_key_after == sub_key_before, sub_key_after

    # .. this server has one queue for the connection and not two ..
    outgoing_sub_keys = server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
    assert outgoing_sub_keys == [sub_key_before], outgoing_sub_keys

    # .. that queue is subscribed to one topic, the one of the new name ..
    sub_rows = get_sub_rows(sub_key_after)
    new_topic = get_outgoing_topic_name(_conn_type, _name_orders_renamed)

    assert len(sub_rows) == 1, sub_rows
    assert sub_rows[0].topic_name == new_topic, sub_rows[0].topic_name

    # .. and what is published after the rename goes to that same queue.
    _ = publisher.publish('Order after')

    def has_both_messages() -> 'bool':
        out = connection.received == ['Order before', 'Order after']
        return out

    _wait_until(has_both_messages, 'the connection receives what was published after the rename')

    outgoing_sub_keys = server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
    assert outgoing_sub_keys == [sub_key_before], outgoing_sub_keys

    delivery.stop()

# ################################################################################################################################

def _run_rename_keeps_order_flow() -> 'None':
    """ Messages published before a rename and after it arrive in the order they were published in.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)

    expected:'anylist' = []

    # Nothing is delivered while the connection is down, so everything published here waits ..
    for index in range(_message_count):
        data = f'Order before {index}'
        expected.append(data)
        _ = publisher.publish(data)

    def is_retrying() -> 'bool':
        out = connection.attempt_count > 0
        return out

    _wait_until(is_retrying, 'the messages are being retried')

    # .. the rename happens in the middle of that ..
    _rename_connection(server, _conn_id_orders, _name_orders_renamed)

    # .. more is published afterwards, to the topic of the new name ..
    for index in range(_message_count):
        data = f'Order after {index}'
        expected.append(data)
        _ = publisher.publish(data)

    # .. and the connection comes back up.
    connection.refuses_everything = False

    def has_everything() -> 'bool':
        count = len(connection.received)
        out = count == len(expected)
        return out

    _wait_until(has_everything, 'the connection receives everything published to it')

    assert connection.received == expected, connection.received

    delivery.stop()

# ################################################################################################################################

def _run_rename_crash_flow() -> 'None':
    """ A rename that a crash interrupted halfway through is finished when the server starts again.
    """
    delete_all_rows()

    _, first_server, first_delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(first_server), _conn_type, _conn_id_orders)

    expected:'anylist' = []

    for index in range(_message_count):
        data = f'Order {index}'
        expected.append(data)
        _ = publisher.publish(data)

    def is_retrying() -> 'bool':
        out = connection.attempt_count > 0
        return out

    _wait_until(is_retrying, 'the messages are being retried')

    # The process ends in the middle of a rename - the messages moved to the new topic,
    # the deliveries and the subscription did not ..
    first_delivery.stop()

    old_topic = get_outgoing_topic_name(_conn_type, _name_orders)
    new_topic = get_outgoing_topic_name(_conn_type, _name_orders_renamed)

    connection.name = _name_orders_renamed
    move_message_rows(old_topic, new_topic)

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    sub_rows = get_sub_rows(sub_key)

    assert sub_rows[0].topic_name == old_topic, sub_rows[0].topic_name

    # .. a server starting up finds the queue and finishes what the rename did not ..
    _, second_server, second_delivery = _new_server()
    second_server.config_manager.restore_outgoing_subscriptions()

    # .. so the whole queue is under the topic of the name the connection goes by now ..
    sub_rows = get_sub_rows(sub_key)

    assert len(sub_rows) == 1, sub_rows
    assert sub_rows[0].topic_name == new_topic, sub_rows[0].topic_name

    sub_config_list = second_server.config_manager._push_subs[sub_key]
    assert sub_config_list[0]['topic_name'] == new_topic, sub_config_list

    # .. the connection is back up by the time the new greenlets run ..
    connection.refuses_everything = False

    for restored_sub_key in second_server.config_manager._push_subs:
        second_delivery.start_sub_key(restored_sub_key)

    def has_everything() -> 'bool':
        count = len(connection.received)
        out = count == len(expected)
        return out

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(sub_key)
        out = not rows
        return out

    # .. and every message queued before the crash arrives, in the order it was published in.
    _wait_until(has_everything, 'everything queued before the crash is delivered')
    _wait_until(has_empty_queue, 'the queue empties out')

    assert connection.received == expected, connection.received

    second_delivery.stop()

# ################################################################################################################################

def _run_delete_flow() -> 'None':
    """ A deleted connection takes its queue with it, along with what that queue still held.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    connection = _new_connection(_conn_id_orders, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    _ = publisher.publish('Order 1234')

    def is_retrying() -> 'bool':
        out = connection.attempt_count > 0
        return out

    # The message is in the queue of a connection that is not taking anything ..
    _wait_until(is_retrying, 'the message is being retried')

    sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    topic_name = get_outgoing_topic_name(_conn_type, _name_orders)

    # .. and then that connection is deleted ..
    _delete_connection(server, _conn_id_orders)

    # .. its greenlet is gone ..
    assert sub_key not in delivery._greenlets, delivery._greenlets

    # .. so is everything this server knew about the queue ..
    assert sub_key not in server.config_manager._push_subs, server.config_manager._push_subs
    assert sub_key not in server.config_manager._outgoing_sub_key_cache, server.config_manager._outgoing_sub_key_cache

    # .. nothing is left of it in the database either, neither its rows nor its subscription ..
    assert not get_delivery_rows(sub_key), get_delivery_rows(sub_key)
    assert not get_sub_rows(sub_key), get_sub_rows(sub_key)
    assert not get_message_rows(topic_name), get_message_rows(topic_name)

    outgoing_sub_keys = server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
    assert not outgoing_sub_keys, outgoing_sub_keys

    # .. and the connection is left alone from then on, because it is not even there to be delivered to.
    attempt_count_at_deletion = connection.attempt_count
    sleep(_quiet_period_seconds)

    assert connection.attempt_count == attempt_count_at_deletion, connection.attempt_count
    assert not connection.received, connection.received

    delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def _run_type_isolation_flow() -> 'None':
    """ Two types of connection sharing one name and one id have a queue each, and neither of them
    is ever given what the other was published to with.
    """
    delete_all_rows()

    _, server, delivery = _new_server()

    # The same name and the same id under two different types, which is all that keeps them apart
    first = _new_connection(_conn_id_orders, _name_orders)
    second = _new_other_connection(_conn_id_orders, _name_orders)

    first_publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id_orders)
    second_publisher = OutgoingPublisher(_as_server(server), _other_conn_type, _conn_id_orders)

    first_expected:'anylist' = []
    second_expected:'anylist' = []

    for index in range(_message_count):

        first_data = f'Order {index}'
        first_expected.append(first_data)
        _ = first_publisher.publish(first_data)

        second_data = f'Archive {index}'
        second_expected.append(second_data)
        _ = second_publisher.publish(second_data)

    def has_everything() -> 'bool':
        out = len(first.received) == _message_count and len(second.received) == _message_count
        return out

    # Each of them receives everything that was published to it ..
    _wait_until(has_everything, 'both connections receive everything published to them')

    # .. and nothing that was published to the other one ..
    assert first.received == first_expected, first.received
    assert second.received == second_expected, second.received

    # .. because the two are queues of their own, one per type ..
    first_sub_key = get_outgoing_sub_key(_conn_type, _conn_id_orders)
    second_sub_key = get_outgoing_sub_key(_other_conn_type, _conn_id_orders)

    assert first_sub_key != second_sub_key, first_sub_key

    outgoing_sub_keys = server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
    assert sorted(outgoing_sub_keys) == sorted([first_sub_key, second_sub_key]), outgoing_sub_keys

    # .. each subscribed to the topic of its own type.
    first_topic = get_outgoing_topic_name(_conn_type, _name_orders)
    second_topic = get_outgoing_topic_name(_other_conn_type, _name_orders)

    assert first_topic != second_topic, first_topic

    first_sub_rows = get_sub_rows(first_sub_key)
    second_sub_rows = get_sub_rows(second_sub_key)

    assert len(first_sub_rows) == 1, first_sub_rows
    assert len(second_sub_rows) == 1, second_sub_rows

    assert first_sub_rows[0].topic_name == first_topic, first_sub_rows[0].topic_name
    assert second_sub_rows[0].topic_name == second_topic, second_sub_rows[0].topic_name

    delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def run_outgoing_scenario() -> 'None':
    """ Publishing to an outgoing connection over the shared backend - a publication reaches the
    connection it named, each connection has a queue of its own, a refused message is offered
    again, an expired one is not, what a stopped process left behind is delivered when it starts
    again, and messages arrive in the order they were published in. A renamed connection keeps
    the one queue it had, with everything in it, a deleted one takes its queue with it, and two
    types sharing one name have a queue each.
    """
    register_outgoing_conn_type(_conn_type, _locate_test_connection, _deliver_to_test_connection)
    register_outgoing_conn_type(_other_conn_type, _locate_other_test_connection, _deliver_to_test_connection)

    _run_publish_delivers_flow()
    _run_queue_isolation_flow()
    _run_retry_then_success_flow()
    _run_expiration_flow()
    _run_restart_recovery_flow()
    _run_ordering_flow()
    _run_rename_flow()
    _run_rename_during_delivery_flow()
    _run_rename_one_queue_flow()
    _run_rename_keeps_order_flow()
    _run_rename_crash_flow()
    _run_delete_flow()
    _run_type_isolation_flow()

# ################################################################################################################################
# ################################################################################################################################
