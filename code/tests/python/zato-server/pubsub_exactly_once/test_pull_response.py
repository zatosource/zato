# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The response of a pull through the REST API, its envelope and every key of each message, for a message published
# with every field and for one published with none.

# stdlib
import json
import time
from http.client import OK

# SQLAlchemy
from sqlalchemy import select

# Zato
from pubsub_exactly_once.harness import get_engine
from pubsub_exactly_once.rest import ack, drain, publish, pull_raw
from zato.common.pubsub.sql.pull import message_payload
from zato.common.pubsub.sql.schema import delivery_table, message_table
from zato.common.test.exactly_once.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_exactly_once.rest import RawResult
    from zato.common.typing_ import any_, anydict, strset

    any_ = any_
    anydict = anydict
    RawResult = RawResult
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The topic that the orders client pulls from
_orders_topic = 'orders'

# The status of a successful response
_status_ok = '200 OK'

# How long a leased message waits for its lease to run out, in seconds
_lease_wait_seconds = 3.0

# The values of a message published with every field
_priority      = 7
_expiration    = 3600
_correl_id     = 'correl-pull-response-1'
_in_reply_to   = 'msg-request-pull-response-1'
_ext_client_id = 'client-maria-johnson'

# The priority that a message published without one receives
_default_priority = 5

# A JSON object payload and a payload of non-ASCII text
_payload_object:'anydict' = {'key': 'pull-response', 'customer': 'Anna Müller', 'amount': 99.95}
_payload_object_text = '{"key": "pull-response", "customer": "Anna M\\u00fcller", "amount": 99.95}'
_payload_text = 'Zamówienie dla Marii Johnson – 5,50 € Jürgen'

# The keys of the envelope of a pull response
_envelope_keys:'strset' = {'is_ok', 'cid', 'messages', 'message_count', 'status'}

# The keys of a message and of its meta
_message_keys:'strset' = {'data', 'meta'}

_base_meta_keys:'strset' = {
    'topic_name',
    'size',
    'priority',
    'expiration',
    'msg_id',
    'delivery_attempt',
    'sub_key',
    'pub_time_iso',
    'recv_time_iso',
    'expiration_time_iso',
    'time_since_pub',
    'time_since_recv',
}

# The correlation ID of a message published without one is the CID of its request
_no_field_meta_keys = _base_meta_keys | {'correl_id'}

_every_field_meta_keys = _base_meta_keys | {'correl_id', 'in_reply_to', 'ext_client_id'}

# ################################################################################################################################
# ################################################################################################################################

def _get_message_row(msg_id:'str') -> 'any_':
    """ Returns the message row of a message ID, with the payload that it references in the payload table
    of the audit log, and the sub key of its only delivery row.
    """
    engine = get_engine()

    query = select(message_table, message_payload, delivery_table.c.sub_key)
    query = query.select_from(message_table.join(delivery_table, delivery_table.c.message_id == message_table.c.id))
    query = query.where(message_table.c.msg_id == msg_id)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    assert len(rows) == 1, rows

    out = rows[0]
    return out

# ################################################################################################################################

def _get_seconds(time_since:'str') -> 'float':
    """ Returns the number of seconds of a time since, in the form of a timedelta as text, e.g. 0:00:01.250000.
    """
    hours, minutes, seconds = time_since.split(':')

    out = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return out

# ################################################################################################################################

def _pull() -> 'RawResult':
    """ Pulls as the orders client and returns the response as the server sent it.
    """
    out = pull_raw(TestConfig.orders_username, TestConfig.orders_password)

    assert out.status_code == OK, out
    return out

# ################################################################################################################################

def _assert_envelope(body:'anydict', message_count:'int') -> 'None':
    """ The envelope of a successful pull with the given number of messages.
    """
    assert set(body) == _envelope_keys, set(body) ^ _envelope_keys
    assert body['is_ok'] is True
    assert isinstance(body['cid'], str)
    assert body['cid']
    assert body['status'] == _status_ok
    assert body['message_count'] == message_count
    assert len(body['messages']) == message_count

# ################################################################################################################################

def _assert_meta_from_row(meta:'anydict', row:'any_', window_seconds:'float') -> 'None':
    """ The values of the meta that the message row stores, and the times since, within the window of the pull.
    """
    assert meta['topic_name'] == _orders_topic
    assert meta['msg_id'] == row.msg_id
    assert meta['size'] == row.data_size
    assert meta['expiration'] == row.expiration
    assert meta['sub_key'] == row.sub_key
    assert meta['pub_time_iso'] == row.pub_time_iso
    assert meta['recv_time_iso'] == row.recv_time_iso
    assert meta['expiration_time_iso'] == row.expiration_time_iso
    assert meta['delivery_attempt'] == 1

    time_since_pub = _get_seconds(meta['time_since_pub'])
    time_since_recv = _get_seconds(meta['time_since_recv'])

    assert 0 <= time_since_pub <= window_seconds, (meta['time_since_pub'], window_seconds)
    assert 0 <= time_since_recv <= window_seconds, (meta['time_since_recv'], window_seconds)

# ################################################################################################################################

def _drain_orders() -> 'None':
    """ Removes what the earlier tests left in the queue of the orders client, including the messages
    whose leases had not run out yet when the first drain ran.
    """
    _ = drain(TestConfig.orders_username, TestConfig.orders_password)

    time.sleep(_lease_wait_seconds)

    _ = drain(TestConfig.orders_username, TestConfig.orders_password)

# ################################################################################################################################
# ################################################################################################################################

def test_pull_response(zato_server:'any_') -> 'None':
    """ A pull of a message published with every field and of one published with none has the envelope
    and every key of each message, with the payloads as the database stores them.
    """
    _drain_orders()

    window_start = time.monotonic()

    # A message with every field ..
    every_field:'anydict' = {
        'data': _payload_object,
        'priority': _priority,
        'expiration': _expiration,
        'correl_id': _correl_id,
        'in_reply_to': _in_reply_to,
        'ext_client_id': _ext_client_id,
    }

    every_field_result = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, every_field)
    assert every_field_result.status_code == OK, every_field_result

    # .. and a message with none ..
    no_field:'anydict' = {'data': _payload_text}

    no_field_result = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, no_field)
    assert no_field_result.status_code == OK, no_field_result

    # .. are pulled together, the one with the higher priority first.
    result = _pull()
    window_seconds = time.monotonic() - window_start

    body = json.loads(result.text)
    _assert_envelope(body, 2)

    every_field_message, no_field_message = body['messages']

    assert set(every_field_message) == _message_keys
    assert set(no_field_message) == _message_keys

    # The message with every field has every key of the meta, with the values given ..
    every_field_row = _get_message_row(every_field_result.body['msg_id'])
    every_field_meta = every_field_message['meta']

    assert set(every_field_meta) == _every_field_meta_keys, set(every_field_meta) ^ _every_field_meta_keys
    assert every_field_meta['msg_id'] == every_field_result.body['msg_id']
    assert every_field_meta['priority'] == _priority
    assert every_field_meta['expiration'] == _expiration
    assert every_field_meta['correl_id'] == _correl_id
    assert every_field_meta['in_reply_to'] == _in_reply_to
    assert every_field_meta['ext_client_id'] == _ext_client_id
    assert every_field_meta['size'] == len(_payload_object_text)

    _assert_meta_from_row(every_field_meta, every_field_row, window_seconds)

    # .. and its JSON object payload is the text that the database stores, placed in the response as it stands.
    assert every_field_row.payload == _payload_object_text
    assert every_field_message['data'] == _payload_object
    assert f'"data":{_payload_object_text}' in result.text

    # The message with no field has the keys of the meta that are always present, with the CID of its request
    # .. as its correlation ID ..
    no_field_row = _get_message_row(no_field_result.body['msg_id'])
    no_field_meta = no_field_message['meta']

    assert set(no_field_meta) == _no_field_meta_keys, set(no_field_meta) ^ _no_field_meta_keys
    assert no_field_meta['msg_id'] == no_field_result.body['msg_id']
    assert no_field_meta['priority'] == _default_priority
    assert no_field_row.cid
    assert no_field_meta['correl_id'] == no_field_row.cid
    assert no_field_row.correl_id == no_field_row.cid
    assert no_field_meta['size'] == len(_payload_text)

    _assert_meta_from_row(no_field_meta, no_field_row, window_seconds)

    # .. and its non-ASCII text arrives unchanged.
    assert no_field_row.payload == _payload_text
    assert no_field_message['data'] == _payload_text

    # Both messages are acknowledged ..
    msg_ids = [every_field_meta['msg_id'], no_field_meta['msg_id']]
    ack_result = ack(TestConfig.orders_username, TestConfig.orders_password, msg_ids)

    assert ack_result.status_code == OK, ack_result

    # .. so the next pull has the envelope of a pull without messages.
    result = _pull()
    body = json.loads(result.text)

    _assert_envelope(body, 0)

# ################################################################################################################################
# ################################################################################################################################
