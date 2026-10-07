# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep, spawn

# Zato
from common import delete_all_rows, get_delivery_rows
from outgoing import _as_server, _deliver_to_test_connection, _hold_seconds, _locate_test_connection, _name_orders, \
    _new_connection, _new_server, _stop_all_deliveries, _wait_until
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.outgoing import get_outgoing_sub_key, OutgoingPublisher, register_outgoing_conn_type, SendResult
from zato.common.typing_ import cast_
from zato.common.util.retry import RetryPolicy
from zato.server.base.parallel import delivery as delivery_module
from zato.server.service.internal.pubsub.browse import MessageAction

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# A type of its own, with one retry, so that a refused direct attempt goes to the queue
_conn_type = 'queue-order-test'
_conn_id = 31

_sub_key = get_outgoing_sub_key(_conn_type, _conn_id)

# How long a direct attempt takes before it is refused, in seconds
_attempt_seconds = 0.2

# How long a paused delivery is waited for before it is stopped, in seconds
_pause_join_timeout = 0.5

# A priority below the default one
_low_priority = 3

# How quickly the expiring message expires, in seconds
_short_expiration_seconds = 1

# ################################################################################################################################
# ################################################################################################################################

def _retry_policy(wrapper:'any_') -> 'RetryPolicy':
    """ One retry after the first attempt.
    """
    config = {HTTP_SOAP.Retry.Field_Max_Retries: 1}

    out = RetryPolicy.from_config(config, HTTP_SOAP.Retry)
    return out

# ################################################################################################################################

class _BrowseService:
    """ What the discard action reads from the service it runs in.
    """

    def __init__(self, server:'any_') -> 'None':
        self.server = server

# ################################################################################################################################
# ################################################################################################################################

def _run_concurrent_sends_flow() -> 'None':
    """ Two sends at once to a connection with an empty queue make one direct attempt at a time.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_id, _name_orders)

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)

    in_flight = [0]
    max_in_flight = [0]

    def attempt() -> 'None':
        in_flight[0] += 1
        max_in_flight[0] = max(max_in_flight[0], in_flight[0])
        sleep(_attempt_seconds)
        in_flight[0] -= 1
        raise Exception('The endpoint did not acknowledge the message')

    first = spawn(publisher.send_or_queue, 'cid-1', {'data': 'Order 1001'}, attempt)
    second = spawn(publisher.send_or_queue, 'cid-2', {'data': 'Order 1002'}, attempt)

    first.join()
    second.join()

    first_result = cast_(SendResult, first.value)
    second_result = cast_(SendResult, second.value)

    # The second send waited for the first one, which queued its message before the second read the depth ..
    assert max_in_flight[0] == 1, max_in_flight

    # .. so both messages are in the queue ..
    assert first_result.is_in_queue, first_result
    assert second_result.is_in_queue, second_result

    def has_both() -> 'bool':
        out = len(connection.received) == 2
        return out

    # .. and both are delivered from there.
    _wait_until(has_both, 'the connection receives both messages from the queue')

    delivery.stop()

# ################################################################################################################################

def _run_publication_order_flow() -> 'None':
    """ A message published with a priority of its own is delivered in its turn, not ahead of the messages before it.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_id, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)
    _ = publisher.publish('Order 1001', priority=_low_priority)

    def has_round_failed() -> 'bool':
        out = connection.attempt_count >= 2
        return out

    # The first message fails both attempts of its round ..
    _wait_until(has_round_failed, 'the first message fails its round')

    # .. the second one is published while the first waits for its next round ..
    _ = publisher.publish('Order 1002')
    connection.refuses_everything = False

    def has_both() -> 'bool':
        out = len(connection.received) == 2
        return out

    _wait_until(has_both, 'the connection receives both messages')

    # .. and the first one is delivered first.
    assert connection.received == ['Order 1001', 'Order 1002'], connection.received

    delivery.stop()

# ################################################################################################################################

def _run_expired_message_flow() -> 'None':
    """ A message that expires in the queue is concluded in its turn and leaves the queue and its depth.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_id, _name_orders)
    connection.refusals_left = 1

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)
    _ = publisher.publish('Order 1001')

    def has_first_attempt() -> 'bool':
        out = connection.attempt_count > 0
        return out

    # The head is refused once, and while it waits for its retry ..
    _wait_until(has_first_attempt, 'the head is attempted')

    # .. a message that expires is published behind it, and one more behind that ..
    _ = publisher.publish('Order 1002', expiration=_short_expiration_seconds)
    _ = publisher.publish('Order 1003')

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(_sub_key)
        out = not rows
        return out

    # .. the queue empties, the expired message included ..
    _wait_until(has_empty_queue, 'the queue empties')

    # .. the expired message never reached the connection ..
    assert connection.received == ['Order 1001', 'Order 1003'], connection.received

    # .. and the depth counts nothing left.
    depth = server.config_manager.outgoing_queue_depth.get(_sub_key)
    assert depth == 0, depth

    delivery.stop()

# ################################################################################################################################

def _run_discard_after_stopped_delivery_flow() -> 'None':
    """ A message delivered in a batch that is stopped before the batch ends is counted out of the queue once,
    and a discard of it afterwards counts nothing more.
    """
    delete_all_rows()

    _, server, delivery = _new_server()
    connection = _new_connection(_conn_id, _name_orders)
    connection.refuses_everything = True
    connection.hold_seconds = _hold_seconds

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)
    first = publisher.publish('Order 1001')
    _ = publisher.publish('Order 1002')

    def has_first_attempt() -> 'bool':
        out = connection.attempt_count > 0
        return out

    # Both messages are in the queue before the first of them goes out ..
    _wait_until(has_first_attempt, 'the first message is attempted')
    connection.refuses_everything = False

    def is_receiving_second() -> 'bool':
        if 'Order 1001' in connection.received:
            out = connection.is_receiving
        else:
            out = False
        return out

    # .. the first one is delivered and the second one is being delivered in the same batch ..
    _wait_until(is_receiving_second, 'the second message is being delivered')

    depth = server.config_manager.outgoing_queue_depth

    # .. the delivery is stopped where it stands, before the batch ends ..
    original_timeout = delivery_module._pause_join_timeout
    delivery_module._pause_join_timeout = _pause_join_timeout

    try:
        browse_service = cast_('MessageAction', _BrowseService(server))
        MessageAction._discard_from_queue(browse_service, _conn_type, _conn_id, _sub_key, [first.msg_id])
    finally:
        delivery_module._pause_join_timeout = original_timeout

    # .. the discard counts out the first message only ..
    depth_after_discard = depth.get(_sub_key)
    assert depth_after_discard == 1, depth_after_discard

    def has_empty_queue() -> 'bool':
        rows = get_delivery_rows(_sub_key)
        out = not rows
        return out

    # .. the second one is delivered again once the queue resumes ..
    _wait_until(has_empty_queue, 'the queue empties')

    # .. and the depth ends at zero.
    depth_at_end = depth.get(_sub_key)
    assert depth_at_end == 0, depth_at_end

    delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def run_queue_order_scenario() -> 'None':
    """ Many messages through the queue of one outgoing connection - concurrent sends, priorities, expiry
    and a delivery stopped in the middle of a batch.
    """
    register_outgoing_conn_type(_conn_type, _locate_test_connection, _deliver_to_test_connection, retry_policy=_retry_policy)

    try:
        _run_concurrent_sends_flow()
        _run_publication_order_flow()
        _run_expired_message_flow()
        _run_discard_after_stopped_delivery_flow()

    finally:
        _stop_all_deliveries()

# ################################################################################################################################
# ################################################################################################################################
