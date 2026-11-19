# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The values of the messages that pulls hand out, key by key, for messages published with every field and with none,
# with payloads of every kind, encrypted at rest, and in the order and within the budget of each pull.

# stdlib
import os
from time import sleep

# Zato
from common import delete_all_rows, delete_audit_rows, get_message_rows
from zato.common.api import HTTP_SOAP
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strset

    any_ = any_
    anydict = anydict
    anylist = anylist
    stranydict = stranydict
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

Env_Pull_Lease_Seconds = ModuleCtx.Env_Pull_Lease_Seconds

# The topics and subscribers of the scenario
_topic_fields  = 'pubsub.backend.test.pull-values.fields'
_topic_retry   = 'pubsub.backend.test.pull-values.retry'
_topic_payload = 'pubsub.backend.test.pull-values.payload'
_topic_crypto  = 'pubsub.backend.test.pull-values.crypto'
_topic_order   = 'pubsub.backend.test.pull-values.order'

_sub_key_fields  = 'zpsk.test.pull-values.fields'
_sub_key_retry   = 'zpsk.test.pull-values.retry'
_sub_key_payload = 'zpsk.test.pull-values.payload'
_sub_key_crypto  = 'zpsk.test.pull-values.crypto'
_sub_key_order   = 'zpsk.test.pull-values.order'

# The values of a message published with every field
_data_fields      = 'Order ORD-0042 for Maria Johnson'
_priority         = 7
_expiration       = 3600
_correl_id        = 'correl-pull-values-1'
_in_reply_to      = 'msg-request-pull-values-1'
_ext_client_id    = 'client-maria-johnson'
_publisher        = 'publisher.orders'
_cid              = 'cid-pull-values-1'
_max_retries      = 3
_retry_sleep_time = 5
_retry_threshold  = 120
_retry_multiplier = 3

# The values of each retry setting when it is published alone
_retry_values:'stranydict' = {
    _retry.Field_Max_Retries: _max_retries,
    _retry.Field_Sleep_Time: _retry_sleep_time,
    _retry.Field_Backoff_Threshold: _retry_threshold,
    _retry.Field_Backoff_Multiplier: _retry_multiplier,
}

# The priority that a message published without one receives
_default_priority = 5

# The keys of a message published with no optional field
_base_keys:'strset' = {
    'msg_id',
    'sequence_id',
    'topic_name',
    'data',
    'data_class',
    'data_size',
    'data_preview',
    'priority',
    'expiration',
    'pub_time_iso',
    'recv_time_iso',
    'expiration_time_iso',
    'delivery_attempt',
}

# The keys that a message published with every field has in addition
_optional_keys:'strset' = {
    'publisher',
    'cid',
    'correl_id',
    'in_reply_to',
    'ext_client_id',
    _retry.Field_Max_Retries,
    _retry.Field_Sleep_Time,
    _retry.Field_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier,
}

# The keys whose values a pull hands out as the message row stores them
_row_keys = ('msg_id', 'pub_time_iso', 'recv_time_iso', 'expiration_time_iso', 'data_size', 'data_preview')

# The payloads of every kind
_payload_dict = {'order': 'ORD-0042', 'customer': 'Anna Müller', 'amount': 99.95}
_payload_dict_text = '{"order": "ORD-0042", "customer": "Anna M\\u00fcller", "amount": 99.95}'
_payload_non_ascii = 'Zamówienie dla Marii Johnson – 5,50 € Jürgen'
_payload_large_line = 'Invoice line for Maria Johnson 42.50 USD\n'
_payload_large = _payload_large_line * 25000
_payload_empty = ''

# The size and preview that the message row of each payload stores
_payload_dict_size = 70
_payload_non_ascii_size = 44
_payload_large_size = 1_025_000
_payload_large_preview = _payload_large_line + _payload_large_line + 'Invoice line for M'

# The budget of the pulls of the order part
_max_len = 50

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    return out

# ################################################################################################################################

def _pull_one(backend:'SQLPubSubBackend', sub_key:'str') -> 'anydict':
    """ Pulls the only message of a subscriber.
    """
    messages = backend.pull_messages(sub_key)

    assert len(messages) == 1, messages

    out = messages[0]
    return out

# ################################################################################################################################

def _assert_row_values(message:'anydict', row:'any_') -> 'None':
    """ The values that a pull reads from the message row are handed out as the row stores them, with their types.
    """
    for key in _row_keys:
        row_value = getattr(row, key)
        assert message[key] == row_value, (key, message[key], row_value)
        assert type(message[key]) is type(row_value), (key, type(message[key]), type(row_value))

    assert message['sequence_id'] == row.id
    assert type(message['sequence_id']) is type(row.id)

# ################################################################################################################################

def _run_every_field(backend:'SQLPubSubBackend') -> 'None':
    """ A message published with every field is handed out with every key, each holding the value given.
    """
    backend.subscribe(_sub_key_fields, _topic_fields)

    result = backend.publish(_topic_fields, _data_fields,
        priority=_priority,
        expiration=_expiration,
        correl_id=_correl_id,
        in_reply_to=_in_reply_to,
        ext_client_id=_ext_client_id,
        publisher=_publisher,
        cid=_cid,
        max_retries=_max_retries,
        retry_sleep_time=_retry_sleep_time,
        retry_backoff_threshold=_retry_threshold,
        retry_backoff_multiplier=_retry_multiplier,
    )

    message = _pull_one(backend, _sub_key_fields)
    rows = get_message_rows(_topic_fields)

    # The message has exactly the keys of all the fields ..
    expected_keys = _base_keys | _optional_keys
    assert set(message) == expected_keys, set(message) ^ expected_keys

    # .. each value given is handed out as it was given ..
    assert message['msg_id'] == result.msg_id
    assert message['topic_name'] == _topic_fields
    assert message['data'] == _data_fields
    assert message['data_class'] == ''
    assert message['priority'] == _priority
    assert message['expiration'] == _expiration
    assert message['correl_id'] == _correl_id
    assert message['in_reply_to'] == _in_reply_to
    assert message['ext_client_id'] == _ext_client_id
    assert message['publisher'] == _publisher
    assert message['cid'] == _cid
    assert message['delivery_attempt'] == 1

    for name, value in _retry_values.items():
        assert message[name] == value, (name, message[name])

    # .. and the values of the row are handed out as it stores them.
    assert len(rows) == 1
    assert rows[0].data_class is None
    assert rows[0].data_size == len(_data_fields)
    assert rows[0].data_preview == _data_fields

    _assert_row_values(message, rows[0])

# ################################################################################################################################

def _run_no_optional_field(backend:'SQLPubSubBackend') -> 'None':
    """ A message published with no optional field is handed out without the keys of those fields.
    """
    backend.subscribe(_sub_key_fields, _topic_fields)

    result = backend.publish(_topic_fields, _data_fields)

    message = _pull_one(backend, _sub_key_fields)
    rows = get_message_rows(_topic_fields)

    # Only the keys that are always present are there ..
    assert set(message) == _base_keys, set(message) ^ _base_keys

    # .. with the default priority and the values of the row.
    assert message['msg_id'] == result.msg_id
    assert message['priority'] == _default_priority
    assert message['delivery_attempt'] == 1

    _assert_row_values(message, rows[0])

# ################################################################################################################################

def _run_retry_settings(backend:'SQLPubSubBackend') -> 'None':
    """ A message published with one retry setting alone is handed out with that retry key alone.
    """
    backend.subscribe(_sub_key_retry, _topic_retry)

    for name, value in _retry_values.items():

        retry_kwargs:'stranydict' = {name: value}
        _ = backend.publish(_topic_retry, _data_fields, **retry_kwargs)

        message = _pull_one(backend, _sub_key_retry)

        expected_keys = _base_keys | {name}
        assert set(message) == expected_keys, (name, set(message) ^ expected_keys)
        assert message[name] == value, (name, message[name])

        # The message is acknowledged so that the next pull hands out the next setting.
        _ = backend.ack_pulled(_sub_key_retry, [message['msg_id']])

# ################################################################################################################################

def _assert_payload(backend:'SQLPubSubBackend', data:'any_', text:'str', size:'int', preview:'str') -> 'None':
    """ A message published with one payload is handed out with the text, size and preview given.
    """
    _ = backend.publish(_topic_payload, data)

    message = _pull_one(backend, _sub_key_payload)

    assert message['data'] == text, message['data'][:100]
    assert message['data_size'] == size, message['data_size']
    assert message['data_preview'] == preview, message['data_preview']
    assert message['data_class'] == ''

    _ = backend.ack_pulled(_sub_key_payload, [message['msg_id']])

# ################################################################################################################################

def _run_payloads(backend:'SQLPubSubBackend') -> 'None':
    """ Payloads of every kind are handed out as the text that the database stored.
    """
    backend.subscribe(_sub_key_payload, _topic_payload)

    # A dict arrives as its JSON text ..
    _assert_payload(backend, _payload_dict, _payload_dict_text, _payload_dict_size, _payload_dict_text)

    # .. non-ASCII text has its size in characters ..
    _assert_payload(backend, _payload_non_ascii, _payload_non_ascii, _payload_non_ascii_size, _payload_non_ascii)

    # .. text of 1 MB has a preview of its first characters ..
    _assert_payload(backend, _payload_large, _payload_large, _payload_large_size, _payload_large_preview)

    # .. and an empty string has no size and no preview.
    _assert_payload(backend, _payload_empty, _payload_empty, 0, '')

# ################################################################################################################################

def _run_encrypted_payload() -> 'None':
    """ A payload encrypted at rest is handed out decrypted.
    """
    delete_all_rows()
    delete_audit_rows()

    secret_key = CryptoManager.generate_key()
    crypto_manager = CryptoManager(secret_key=secret_key)

    backend = SQLPubSubBackend(audit_log=new_test_audit_log(), crypto_manager=crypto_manager, encrypt_at_rest=True)
    backend.subscribe(_sub_key_crypto, _topic_crypto)

    _ = backend.publish(_topic_crypto, _payload_non_ascii)

    # The database stores the payload encrypted ..
    rows = get_message_rows(_topic_crypto)

    assert rows[0].payload_encrypted
    assert rows[0].payload != _payload_non_ascii

    # .. and the pull hands out its text.
    message = _pull_one(backend, _sub_key_crypto)

    assert message['data'] == _payload_non_ascii
    assert message['data_size'] == _payload_non_ascii_size
    assert message['data_preview'] == _payload_non_ascii

# ################################################################################################################################

def _get_data_list(messages:'anylist') -> 'anylist':
    """ Returns the payloads of the messages of one pull, in the order of the pull.
    """
    out:'anylist' = []

    for message in messages:
        out.append(message['data'])

    return out

# ################################################################################################################################

def _run_order_and_budget(backend:'SQLPubSubBackend') -> 'None':
    """ A pull hands out messages by priority and then in the order of publication, within its budget,
    with an oversized message after the messages ahead of it, ending the pull.
    """
    backend.subscribe(_sub_key_order, _topic_order)

    data_low_1 = 'a' * 10
    data_low_2 = 'b' * 20
    data_high = 'c' * 15
    data_oversized = 'd' * 60
    data_after = 'e' * 5

    _ = backend.publish(_topic_order, data_low_1, priority=5)
    _ = backend.publish(_topic_order, data_low_2, priority=5)
    _ = backend.publish(_topic_order, data_high, priority=7)
    _ = backend.publish(_topic_order, data_oversized, priority=5)
    _ = backend.publish(_topic_order, data_after, priority=5)

    # The first pull hands out the highest priority first, then the others in the order of publication,
    # .. and the oversized message ends it ..
    messages = backend.pull_messages(_sub_key_order, max_len=_max_len)
    data_list = _get_data_list(messages)

    assert data_list == [data_high, data_low_1, data_low_2, data_oversized], data_list

    # .. the messages ahead of the oversized one stay within the budget ..
    total_len = 0

    for message in messages[:-1]:
        total_len += message['data_size']

    assert total_len <= _max_len, total_len

    # .. and the next pull hands out what follows.
    messages = backend.pull_messages(_sub_key_order, max_len=_max_len)
    data_list = _get_data_list(messages)

    assert data_list == [data_after], data_list

    # A message that would exceed the budget waits for the next pull.
    data_first = 'f' * 30
    data_second = 'g' * 30

    _ = backend.publish(_topic_order, data_first)
    _ = backend.publish(_topic_order, data_second)

    messages = backend.pull_messages(_sub_key_order, max_len=_max_len)
    data_list = _get_data_list(messages)

    assert data_list == [data_first], data_list

    messages = backend.pull_messages(_sub_key_order, max_len=_max_len)
    data_list = _get_data_list(messages)

    assert data_list == [data_second], data_list

# ################################################################################################################################

def _run_attempts(backend:'SQLPubSubBackend') -> 'None':
    """ A message whose lease ran out is handed out again with the next attempt number.
    """
    backend.subscribe(_sub_key_order, _topic_order)

    result = backend.publish(_topic_order, _data_fields)

    # A lease of zero seconds runs out as soon as the clock moves on ..
    os.environ[Env_Pull_Lease_Seconds] = '0'

    try:
        first = _pull_one(backend, _sub_key_order)
        sleep(0.01)
        second = _pull_one(backend, _sub_key_order)
    finally:
        del os.environ[Env_Pull_Lease_Seconds]

    # .. so the second copy carries the second attempt and the same values otherwise.
    assert first['msg_id'] == result.msg_id
    assert first['delivery_attempt'] == 1
    assert second['delivery_attempt'] == 2

    first_values = dict(first)
    second_values = dict(second)

    del first_values['delivery_attempt']
    del second_values['delivery_attempt']

    assert first_values == second_values

# ################################################################################################################################

def run_pull_values_scenario() -> 'None':
    """ The values of the messages that pulls hand out, each part starting from empty tables.
    """
    _run_every_field(_new_backend())
    _run_no_optional_field(_new_backend())
    _run_retry_settings(_new_backend())
    _run_payloads(_new_backend())
    _run_encrypted_payload()
    _run_order_and_budget(_new_backend())
    _run_attempts(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
