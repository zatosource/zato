# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The push of several messages in one request to a REST endpoint - a JSON list of envelopes, answered with the JSON list
# of the IDs of the messages that the endpoint accepted - under partial acceptances, responses that accept nothing,
# redirects, edits of payloads between two attempts and messages whose retry policy runs out.

# stdlib
import json

# gevent
from gevent.pywsgi import WSGIServer

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_event_rows
from fast_path_common import wait_until
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.test.expected_records import expected_records
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery
from zato.server.base.parallel.delivery_message import logger as delivery_message_logger
from zato.server.base.parallel.delivery_rest import logger as delivery_rest_logger

# Test support
from rest_outgoing_stub.connection import new_connection, ServerStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber of the scenarios
_topic = 'pubsub.backend.test.push-multi'
_sub_key = 'zpsk.test.push-multi.1'

# How many messages one push request of the subscriber holds
_push_batch_size = 3

# The ID of the outgoing REST connection of the endpoint of the subscriber
_endpoint_id = 1

# The address that the receiver listens on, and the paths of the endpoint and of the target of its redirect
_host = '127.0.0.1'
_any_port = 0
_path = '/push-multi'
_path_moved = '/push-multi-moved'

# The payloads of the scenarios
_data_first = 'Order ORD-5001 for John Smith'
_data_second = 'Order ORD-5002 for Maria Johnson'
_data_third = 'Order ORD-5003 for Robert Brown'
_data_edited = 'Order ORD-5002 for Maria Johnson, two items added'

# The retry settings of the messages of the scenarios - a wait of one second that does not grow between attempts
_retry_sleep_time = 1
_retry_backoff_multiplier = 1
_max_retries = 10

# The responses of the receiver
_status_ok = '200 OK'
_status_error = '500 Internal Server Error'
_status_redirect = '307 Temporary Redirect'
_json_headers = [('Content-Type', 'application/json')]

# A message ID that no request names
_unknown_msg_id = 'zpsm.test.push-multi.unknown'

# How long the receiver is given to complete the requests in progress when it stops, in seconds
_stop_timeout = 1

# ################################################################################################################################
# ################################################################################################################################

class _Receiver:
    """ The REST endpoint of the subscriber. It records each request and answers it with the next reply of its script,
    or, once the script is used up, by accepting every message of the request.
    """

    def __init__(self) -> 'None':
        self.requests:'anylist' = []
        self.replies:'anylist' = []
        self.port = 0
        self._server:'any_' = None

    def _handle(self, environ:'anydict', start_response:'callable_') -> 'anylist':

        path = environ['PATH_INFO']
        body = environ['wsgi.input'].read()
        envelopes = json.loads(body)

        self.requests.append((path, envelopes))

        if self.replies:
            reply = self.replies.pop(0)
        else:
            reply = _accept_all

        status, headers, body = reply(envelopes)
        start_response(status, headers)

        return [body]

    def start(self) -> 'None':
        self._server = WSGIServer((_host, _any_port), self._handle, log=None, error_log=None)
        self._server.start()
        self.port = self._server.server_port

    def stop(self) -> 'None':
        self._server.stop(timeout=_stop_timeout)

# ################################################################################################################################

class _OutconnItem:
    """ An outgoing REST connection as the config store holds it, with its address and its connection.
    """
    def __init__(self, base:'str', conn:'HTTPSOAPWrapper') -> 'None':
        self.config = {'host': base, 'url_path': _path}
        self.conn = conn

# ################################################################################################################################

class _OutconnStore:
    """ The outgoing REST connections of the config store, which hold the connection of the subscriber.
    """
    def __init__(self, item:'_OutconnItem') -> 'None':
        self._item = item

    def get_by_id(self, endpoint_id:'int') -> '_OutconnItem':
        return self._item

# ################################################################################################################################

class _StubConfigStore:
    """ The part of the config store that a delivery reads.
    """
    def __init__(self, item:'_OutconnItem') -> 'None':
        self.out_plain_http = _OutconnStore(item)

# ################################################################################################################################

class _StubConfigManager:
    """ Carries the push subscriptions and the config store the way the config manager of the server does.
    """
    def __init__(self, config_store:'_StubConfigStore') -> 'None':
        self._push_subs:'anydict' = {}
        self.config_store = config_store

# ################################################################################################################################

class _StubServer:
    """ Stands in for the server, of which a delivery reads the push subscriptions and the config store.
    """
    def __init__(self, config_store:'_StubConfigStore') -> 'None':
        self.config_manager = _StubConfigManager(config_store)

# ################################################################################################################################
# ################################################################################################################################

def _reply_json(document:'any_') -> 'anytuple':
    """ Returns a reply of HTTP 200 with the document as its JSON body.
    """
    body = json.dumps(document).encode('utf8')

    out = (_status_ok, _json_headers, body)
    return out

# ################################################################################################################################

def _accept_all(envelopes:'anylist') -> 'anytuple':
    """ Accepts every message of a request.
    """
    out = _reply_json(_get_msg_ids(envelopes))
    return out

# ################################################################################################################################

def _accept_first(envelopes:'anylist') -> 'anytuple':
    """ Accepts the first message of a request alone.
    """
    out = _reply_json(_get_msg_ids(envelopes)[:1])
    return out

# ################################################################################################################################

def _accept_none(envelopes:'anylist') -> 'anytuple':
    """ Accepts no message of a request with an empty list.
    """
    out = _reply_json([])
    return out

# ################################################################################################################################

def _reply_not_json(envelopes:'anylist') -> 'anytuple':
    """ Answers with HTTP 200 and a body that is not JSON.
    """
    out = (_status_ok, _json_headers, b'Accepted')
    return out

# ################################################################################################################################

def _reply_not_list(envelopes:'anylist') -> 'anytuple':
    """ Answers with HTTP 200 and a JSON body that is not a list.
    """
    out = _reply_json({'accepted': _get_msg_ids(envelopes)})
    return out

# ################################################################################################################################

def _reply_unknown_id(envelopes:'anylist') -> 'anytuple':
    """ Answers with HTTP 200 and a list that names a message of no request.
    """
    out = _reply_json([_unknown_msg_id])
    return out

# ################################################################################################################################

def _reply_error(envelopes:'anylist') -> 'anytuple':
    """ Answers with HTTP 500 and a list that would accept every message, which a status other than 2xx overrides.
    """
    body = json.dumps(_get_msg_ids(envelopes)).encode('utf8')

    out = (_status_error, _json_headers, body)
    return out

# ################################################################################################################################

def _reply_redirect(envelopes:'anylist') -> 'anytuple':
    """ Redirects a request to the moved path of the endpoint with HTTP 307.
    """
    out = (_status_redirect, [('Location', _path_moved)], b'')
    return out

# ################################################################################################################################

def _get_msg_ids(envelopes:'anylist') -> 'strlist':
    """ Returns the message IDs of the envelopes of a request.
    """
    out:'strlist' = []

    for envelope in envelopes:
        out.append(envelope['msg_id'])

    return out

# ################################################################################################################################

def _get_sent(receiver:'_Receiver') -> 'anylist':
    """ Returns each request received, as its path and the payload and the attempt of each of its messages.
    """
    out:'anylist' = []

    for path, envelopes in receiver.requests:

        messages:'anylist' = []

        for envelope in envelopes:
            messages.append((envelope['data'], envelope['delivery_attempt']))

        out.append((path, messages))

    return out

# ################################################################################################################################

def _get_event_msg_ids(event_type:'str') -> 'strlist':
    """ Returns the message IDs of the audit events of one type of the topic of the scenarios, in their order.
    """
    out:'strlist' = []

    for row in get_event_rows(_topic, event_type):
        out.append(row['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class _Scenario:
    """ A backend over empty tables, the delivery of its subscriber to the receiver and the messages published for it.
    """

    def __init__(self, receiver:'_Receiver') -> 'None':

        delete_all_rows()
        delete_audit_rows()

        receiver.requests.clear()
        receiver.replies.clear()

        self.receiver = receiver
        self.backend = SQLPubSubBackend(audit_log=new_test_audit_log())
        self.backend.subscribe(_sub_key, _topic)

        base = f'http://{_host}:{receiver.port}'
        conn = new_connection(ServerStub(), base, _path)
        config_store = _StubConfigStore(_OutconnItem(base, conn))

        server = _StubServer(config_store)
        server.config_manager._push_subs[_sub_key] = [{
            'sub_key': _sub_key,
            'topic_name': _topic,
            'push_type': PubSub.Push_Type.REST,
            'rest_push_endpoint_id': _endpoint_id,
            'push_batch_size': _push_batch_size,
        }]

        self.delivery = PushDelivery(cast_('ParallelServer', server), self.backend)
        self.msg_ids:'strlist' = []

    def publish(self, data:'str', max_retries:'int'=_max_retries) -> 'None':
        """ Publishes one message with the retry settings of the scenarios.
        """
        result = self.backend.publish(_topic, data, max_retries=max_retries, retry_sleep_time=_retry_sleep_time,
            retry_backoff_multiplier=_retry_backoff_multiplier)

        self.msg_ids.append(result.msg_id)

    def run(self, request_count:'int', on_request:'callable_ | None'=None) -> 'None':
        """ Delivers the messages published so far until the receiver received the given number of requests and the queue
        of the subscriber is empty, calling on_request once the first request was received.
        """
        def _is_concluded() -> 'bool':
            if len(self.receiver.requests) == request_count:
                out = get_delivery_rows(_sub_key) == []
            else:
                out = False

            return out

        try:
            self.delivery.start_sub_key(_sub_key)

            if on_request:
                wait_until(lambda: len(self.receiver.requests) > 0, 'the first request is received')
                on_request()

            wait_until(_is_concluded, f'{request_count} requests conclude every message')

        finally:
            self.delivery.stop()

# ################################################################################################################################
# ################################################################################################################################

def _run_all_concluded(receiver:'_Receiver') -> 'None':
    """ A request whose response names all of its messages concludes each of them as delivered.
    """
    scenario = _Scenario(receiver)

    scenario.publish(_data_first)
    scenario.publish(_data_second)
    scenario.publish(_data_third)

    scenario.run(1)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1), (_data_third, 1)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

    delivered = _get_event_msg_ids(AuditEvent.Delivered)
    assert delivered == scenario.msg_ids, delivered

# ################################################################################################################################

def _run_partial(receiver:'_Receiver') -> 'None':
    """ A response that names some of the messages concludes them alone, and the rest go out in the next request,
    in their order, with their next attempt.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_accept_first)

    scenario.publish(_data_first)
    scenario.publish(_data_second)
    scenario.publish(_data_third)

    scenario.run(2)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1), (_data_third, 1)]),
        (_path, [(_data_second, 2), (_data_third, 2)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

# ################################################################################################################################

def _run_empty_list(receiver:'_Receiver') -> 'None':
    """ A response with an empty list concludes no message, and the whole group goes out again.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_accept_none)

    scenario.publish(_data_first)
    scenario.publish(_data_second)

    scenario.run(2)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1)]),
        (_path, [(_data_first, 2), (_data_second, 2)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

# ################################################################################################################################

def _run_invalid_responses(receiver:'_Receiver') -> 'None':
    """ A response that is not JSON, that is not a list or that names a message of no request concludes no message.
    """
    scenario = _Scenario(receiver)
    receiver.replies.extend([_reply_not_json, _reply_not_list, _reply_unknown_id])

    scenario.publish(_data_first)
    scenario.publish(_data_second)

    with expected_records(delivery_rest_logger.name):
        scenario.run(4)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1)]),
        (_path, [(_data_first, 2), (_data_second, 2)]),
        (_path, [(_data_first, 3), (_data_second, 3)]),
        (_path, [(_data_first, 4), (_data_second, 4)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

# ################################################################################################################################

def _run_status_error(receiver:'_Receiver') -> 'None':
    """ A response with a status other than 2xx concludes no message, whatever its body names.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_reply_error)

    scenario.publish(_data_first)
    scenario.publish(_data_second)

    scenario.run(2)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1)]),
        (_path, [(_data_first, 2), (_data_second, 2)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

# ################################################################################################################################

def _run_redirect(receiver:'_Receiver') -> 'None':
    """ A request redirected with HTTP 307 goes to the new location with the same list of envelopes.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_reply_redirect)

    scenario.publish(_data_first)
    scenario.publish(_data_second)

    scenario.run(2)

    first_path, first_envelopes = receiver.requests[0]
    second_path, second_envelopes = receiver.requests[1]

    assert first_path == _path, first_path
    assert second_path == _path_moved, second_path
    assert second_envelopes == first_envelopes, (first_envelopes, second_envelopes)

    delivered = _get_event_msg_ids(AuditEvent.Delivered)
    assert delivered == scenario.msg_ids, delivered

# ################################################################################################################################

def _run_edited(receiver:'_Receiver') -> 'None':
    """ A payload edited between two attempts of a group goes out in its new form with the next attempt.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_accept_none)

    scenario.publish(_data_first)
    scenario.publish(_data_second)

    def _edit() -> 'None':
        assert scenario.backend.update_message(_topic, scenario.msg_ids[1], _data_edited)

    scenario.run(2, _edit)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1)]),
        (_path, [(_data_first, 2), (_data_edited, 2)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

# ################################################################################################################################

def _run_exhausted(receiver:'_Receiver') -> 'None':
    """ A message of a group whose retry policy allows no more attempts leaves the group as a failed delivery,
    and the rest of the group goes out again.
    """
    scenario = _Scenario(receiver)
    receiver.replies.append(_reply_error)

    scenario.publish(_data_first, max_retries=0)
    scenario.publish(_data_second)
    scenario.publish(_data_third)

    with expected_records(delivery_message_logger.name):
        scenario.run(2)

    expected = [
        (_path, [(_data_first, 1), (_data_second, 1), (_data_third, 1)]),
        (_path, [(_data_second, 2), (_data_third, 2)]),
    ]

    sent = _get_sent(receiver)
    assert sent == expected, sent

    failed = _get_event_msg_ids(AuditEvent.Delivery_Failed)
    assert failed == scenario.msg_ids[:1], failed

    delivered = _get_event_msg_ids(AuditEvent.Delivered)
    assert delivered == scenario.msg_ids[1:], delivered

# ################################################################################################################################
# ################################################################################################################################

def run_push_multi_scenario() -> 'None':
    """ Several messages of a push subscriber in each request to its REST endpoint.
    """
    receiver = _Receiver()
    receiver.start()

    try:
        _run_all_concluded(receiver)
        _run_partial(receiver)
        _run_empty_list(receiver)
        _run_invalid_responses(receiver)
        _run_status_error(receiver)
        _run_redirect(receiver)
        _run_edited(receiver)
        _run_exhausted(receiver)

    finally:
        receiver.stop()

# ################################################################################################################################
# ################################################################################################################################
