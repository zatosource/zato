# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# gevent
from gevent import sleep

# Zato
from common import delete_all_rows
from outgoing import _as_server, _deliver_to_test_connection, _locate_test_connection, _name_orders, _new_connection, \
    _StubServer, _deliveries, _stop_all_deliveries, _wait_until
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name, Header_Rounds, Key_DLQ
from zato.common.pubsub.outgoing import OutgoingPublisher, register_outgoing_conn_type
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.typing_ import cast_
from zato.common.util.retry import RetryPolicy
from zato.common.util.time_ import utcnow
from zato.server.base.parallel.delivery import PushDelivery
from zato.server.service.internal.pubsub.dlq import DLQRun, RetryMessage
from zato.server.service.internal.pubsub.outgoing import Deliver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

# A type of its own, whose connection has a DLQ and the retry action
_conn_type = 'dlq-rule-test'
_conn_id = 37

# How long the DLQ is watched for a message the rule should not have put back, in seconds
_quiet_period_seconds = 2

# The DLQ settings of the connection, which each flow sets to what it needs
_settings:'stranydict' = {
    _dlq.Field_Use_DLQ: True,
    _dlq.Field_Action: _dlq.Action.Retry,
    _dlq.Field_Retries: 1,
    _dlq.Field_Retry_Interval: 0,
    _dlq.Field_Forward_To: '',
    _dlq.Field_Keep_Header: True,
}

# ################################################################################################################################
# ################################################################################################################################

def _get_dlq_sub_key() -> 'str':
    """ The sub key of the DLQ of the connection, which exists once its type is registered.
    """
    out = get_dlq_sub_key(_conn_type, _conn_id)
    return out

# ################################################################################################################################

def _retry_policy(wrapper:'any_') -> 'RetryPolicy':
    """ The default retry policy, with which one round is one attempt.
    """
    out = RetryPolicy.from_config({}, HTTP_SOAP.Retry)
    return out

# ################################################################################################################################

def _dlq_settings(wrapper:'any_') -> 'stranydict':
    """ The DLQ settings the connection has.
    """
    return _settings

# ################################################################################################################################

class _Request:
    """ What a service reads of the request it was invoked with.
    """

    def __init__(self, raw_request:'any_', input:'any_') -> 'None':
        self.raw_request = raw_request
        self.input = input

# ################################################################################################################################

class _RetryInput:
    """ The input of an operator's retry of one DLQ message.
    """

    def __init__(self, sub_key:'str', msg_id:'str') -> 'None':
        self.sub_key = sub_key
        self.msg_id = msg_id

# ################################################################################################################################

class _Response:
    """ What a service writes its response to.
    """
    payload:'any_' = None

# ################################################################################################################################

class _DeliveringServer(_StubServer):
    """ A server whose invoke runs the delivery service, which moves a message whose round failed to the DLQ.
    """

    def invoke(self, service_name:'str', payload:'str') -> 'None':

        self.invoked.append(service_name)

        service = object.__new__(Deliver)
        service.server = _as_server(self)
        service.cid = 'test-cid'
        service.request = cast_('any_', _Request(payload, None))

        Deliver.handle(service)

# ################################################################################################################################

def _new_server() -> '_DeliveringServer':
    """ A server with the delivery greenlets of one process.
    """
    backend = SQLPubSubBackend()
    server = _DeliveringServer(backend)
    delivery = PushDelivery(_as_server(server), backend)

    server.pubsub_push_delivery = delivery
    _deliveries.append(delivery)

    return server

# ################################################################################################################################

def _new_rule(server:'_DeliveringServer') -> 'DLQRun':
    """ The DLQ rule, as the scheduler's job runs it.
    """
    out = object.__new__(DLQRun)
    out.server = _as_server(server)

    return out

# ################################################################################################################################

def _retry_by_operator(server:'_DeliveringServer', msg_id:'str') -> 'None':
    """ An operator's retry of one DLQ message.
    """
    service = object.__new__(RetryMessage)
    service.server = _as_server(server)
    dlq_sub_key = _get_dlq_sub_key()
    retry_input = _RetryInput(dlq_sub_key, msg_id)

    service.request = cast_('any_', _Request(None, retry_input))
    service.response = cast_('any_', _Response())

    service.handle()

# ################################################################################################################################

def _get_dlq_messages(server:'_DeliveringServer') -> 'anylist':
    """ Every message the DLQ of the connection holds, each as its id and its document.
    """
    dlq_sub_key = _get_dlq_sub_key()
    dlq_topic_name = get_dlq_topic_name(_conn_type, _name_orders)

    messages, _ = server.pubsub_backend.browse_messages(dlq_topic_name, dlq_sub_key, 'pending', needs_data=True)

    out:'anylist' = []

    for message in messages:
        document = loads(message['data'])
        out.append((message['msg_id'], document))

    return out

# ################################################################################################################################

def _wait_for_one_dlq_message(server:'_DeliveringServer', rounds:'int') -> 'anytuple':
    """ Blocks until the DLQ holds one message with that many rounds, then returns its id and its document.
    """
    found:'anylist' = []

    def has_message() -> 'bool':
        messages = _get_dlq_messages(server)
        message_count = len(messages)

        if message_count == 1:
            message = messages[0]
            _, document = message
            out = document[Key_DLQ][Header_Rounds] == rounds
            if out:
                found.append(message)
        else:
            out = False

        return out

    _wait_until(has_message, f'the DLQ holds one message with {rounds} rounds')

    out = found[0]
    return out

# ################################################################################################################################

class _RuleReadBeforeOperator(DLQRun):
    """ The DLQ rule, with an operator retrying every message of the DLQ right after the rule read them.
    """

    def _get_all_documents(self, topic_name:'str', sub_key:'str') -> 'anylist':

        # The rule reads the DLQ ..
        out = super()._get_all_documents(topic_name, sub_key)
        server = cast_('_DeliveringServer', self.server)

        # .. an operator retries each message it read ..
        for msg_id, _ in out:
            _retry_by_operator(server, msg_id)

        # .. and each of them fails again and is back in the DLQ before the rule acts on what it read.
        _ = _wait_for_one_dlq_message(server, 1)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _run_operator_retry_then_rule_flow() -> 'None':
    """ An operator's retry of a DLQ message leaves every retry of the DLQ rule to the rule.
    """
    delete_all_rows()

    server = _new_server()
    connection = _new_connection(_conn_id, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)
    _ = publisher.publish('Order 1001')

    # The message fails its round and moves to the DLQ ..
    msg_id, _ = _wait_for_one_dlq_message(server, 0)

    # .. an operator retries it and it fails again ..
    _retry_by_operator(server, msg_id)
    _ = _wait_for_one_dlq_message(server, 1)

    attempts_before_rule = connection.attempt_count
    dlq_sub_key = _get_dlq_sub_key()
    rule = _new_rule(server)

    # .. the rule, with one retry allowed, still puts it back once ..
    count = rule._run_for_connection(dlq_sub_key, _conn_type, _name_orders, _settings, utcnow())
    assert count == 1, count

    _ = _wait_for_one_dlq_message(server, 2)
    assert connection.attempt_count > attempts_before_rule, connection.attempt_count

    # .. and then leaves it in the DLQ.
    count = rule._run_for_connection(dlq_sub_key, _conn_type, _name_orders, _settings, utcnow())
    assert count == 0, count

    server.pubsub_push_delivery.stop()

# ################################################################################################################################

def _run_operator_retry_during_rule_flow() -> 'None':
    """ A message an operator retried after the DLQ rule read it is not put back by the rule a second time.
    """
    delete_all_rows()

    server = _new_server()
    connection = _new_connection(_conn_id, _name_orders)
    connection.refuses_everything = True

    publisher = OutgoingPublisher(_as_server(server), _conn_type, _conn_id)
    _ = publisher.publish('Order 1002')

    # The message fails its round and moves to the DLQ ..
    _ = _wait_for_one_dlq_message(server, 0)

    dlq_sub_key = _get_dlq_sub_key()

    rule = object.__new__(_RuleReadBeforeOperator)
    rule.server = _as_server(server)

    # .. the rule reads it, an operator retries it in the meantime, and the rule acts on nothing ..
    count = rule._run_for_connection(dlq_sub_key, _conn_type, _name_orders, _settings, utcnow())
    assert count == 0, count

    sleep(_quiet_period_seconds)

    # .. so the one request is in the DLQ once.
    messages = _get_dlq_messages(server)
    message_count = len(messages)
    assert message_count == 1, messages

    server.pubsub_push_delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def run_dlq_rule_scenario() -> 'None':
    """ The DLQ rule of one outgoing connection next to an operator's retries of the same messages.
    """
    register_outgoing_conn_type(_conn_type, _locate_test_connection, _deliver_to_test_connection,
        retry_policy=_retry_policy, dlq_settings=_dlq_settings)

    try:
        _run_operator_retry_then_rule_flow()
        _run_operator_retry_during_rule_flow()

    finally:
        _stop_all_deliveries()

# ################################################################################################################################
# ################################################################################################################################
