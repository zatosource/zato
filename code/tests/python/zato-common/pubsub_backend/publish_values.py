# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The message rows and delivery rows that publications write, column by column, for messages published with every field
# and with none, with payloads of every form, encrypted at rest, to topics without subscribers, and the publications
# whose message identifiers exist already.

# stdlib
import os
from dataclasses import dataclass
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import event

# Zato
from common import delete_all_rows, delete_audit_rows, env_value, get_delivery_rows, get_message_rows, get_trace_rows, \
    write_in_one_commit
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database import get_database_engine
from zato.common.marshal_.api import Model
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.schema import message_table
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.util.time_ import datetime_to_ms, parse_utc

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import any_, anydict, anylist, strset

    any_ = any_
    anydict = anydict
    anylist = anylist
    BuiltPublication = BuiltPublication
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

Env_Delivered_Max_Messages = ModuleCtx.Env_Delivered_Max_Messages
Env_Dedup_Window_Days = ModuleCtx.Env_Dedup_Window_Days

# The topics and subscribers of the scenario
_topic_fields    = 'pubsub.backend.test.publish-values.fields'
_topic_forms     = 'pubsub.backend.test.publish-values.forms'
_topic_crypto    = 'pubsub.backend.test.publish-values.crypto'
_topic_no_subs   = 'pubsub.backend.test.publish-values.no-subs'
_topic_repeat    = 'pubsub.backend.test.publish-values.repeat'
_topic_other     = 'pubsub.backend.test.publish-values.other'

_sub_key_first  = 'zpsk.test.publish-values.first'
_sub_key_second = 'zpsk.test.publish-values.second'

# The topic as a publisher gives it, which the message row stores in lowercase
_topic_fields_given = 'PubSub.Backend.Test.Publish-Values.Fields'

# The values of a message published with every field
_msg_id_fields    = 'zpsm.test.publish-values.every-field'
_data_fields      = 'Order ORD-0042 for Maria Johnson'
_crc32_fields     = 334252268
_priority         = 7
_expiration       = 3600
_pub_time_iso     = '2026-03-01T10:15:30.250000+00:00'
_pub_time_ms      = 1772360130250
_correl_id        = 'correl-publish-values-1'
_in_reply_to      = 'msg-request-publish-values-1'
_ext_client_id    = 'client-maria-johnson'
_publisher        = 'publisher.orders'
_cid              = 'cid-publish-values-1'
_max_retries      = 3
_retry_sleep_time = 5
_retry_threshold  = 120
_retry_multiplier = 3

# The priority and expiration that a message published without them receives
_default_priority   = 5
_default_expiration = 31_536_000

# The payloads of every form, with the text, checksum, size and preview that the message row stores for each
_payload_dict = {'order': 'ORD-0042', 'customer': 'Anna Müller', 'amount': 99.95}
_payload_dict_text = '{"order": "ORD-0042", "customer": "Anna M\\u00fcller", "amount": 99.95}'
_payload_dict_crc32 = 3453724153
_payload_dict_size = 70

_payload_model_text = '{"order_id":"ORD-0042","customer":"Maria Johnson","amount":9995}'
_payload_model_crc32 = 1933229910
_payload_model_size = 64
_payload_model_class = 'publish_values.OrderRecord'

_payload_non_ascii = 'Zamówienie dla Marii Johnson – 5,50 € Jürgen'
_payload_non_ascii_crc32 = 3659867415
_payload_non_ascii_size = 44

_payload_large_line = 'Invoice line for Maria Johnson 42.50 USD\n'
_payload_large = _payload_large_line * 25000
_payload_large_crc32 = 1984673339
_payload_large_size = 1_025_000
_payload_large_preview = _payload_large_line + _payload_large_line + 'Invoice line for M'

# A payload with a NUL character, which is stored as the Base64 of its UTF-8 bytes, and whose preview holds
# the replacement character in place of the NUL character
_payload_nul = 'Order ORD-0042\x00for Maria Johnson'
_payload_nul_base64 = 'T3JkZXIgT1JELTAwNDIAZm9yIE1hcmlhIEpvaG5zb24='
_payload_nul_crc32 = 1319825628
_payload_nul_size = 32
_payload_nul_preview = 'Order ORD-0042\ufffdfor Maria Johnson'

# The identifier of the message that the publications of the repeat parts share, and the payloads they publish
_msg_id_repeat = 'zpsm.test.publish-values.repeat'
_data_repeat = 'Invoice INV-7781 for John Smith'
_data_different = 'Shipment SHP-1203 for Jane Doe'

# Every column of the message table
_message_columns:'strset' = set(message_table.c.keys())

# The columns of a message row whose values follow from the time of the publication
_time_columns:'strset' = {'id', 'recv_time_iso', 'expiration_time_iso', 'expiration_ms'}

# How many fully delivered messages each topic retains while the cleanup removes the repeated message
_no_delivered_messages = '0'

# The dedup window of a publication whose dedup record expires the moment it is written
_no_dedup_window_days = '0'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OrderRecord(Model):
    order_id: 'str'
    customer: 'str'
    amount: 'int'

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

def get_only_row(topic_name:'str') -> 'anydict':
    """ Returns the values of the only message row of a topic, by column.
    """
    rows = get_message_rows(topic_name)
    assert len(rows) == 1, rows

    only_row = rows[0]

    out = dict(only_row._mapping)
    return out

# ################################################################################################################################

def _get_delivery_values(sub_key:'str') -> 'anylist':
    """ Returns the values of the delivery rows of a subscriber, by column, in the order of their keys.
    """
    out:'anylist' = []

    for row in get_delivery_rows(sub_key):
        values = dict(row._mapping)
        out.append(values)

    return out

# ################################################################################################################################

def assert_message_row(values:'anydict', expected:'anydict', publish_start_ms:'int', publish_end_ms:'int') -> 'None':
    """ A message row has the expected value in each column, with its times those of the database at the publication.
    """
    assert set(values) == _message_columns, set(values) ^ _message_columns

    expected_columns = set(expected) | _time_columns
    assert expected_columns == _message_columns, expected_columns ^ _message_columns

    for name, value in expected.items():
        assert values[name] == value, (name, values[name], value)
        assert type(values[name]) is type(value), (name, type(values[name]), type(value))

    assert values['id'] > 0, values['id']

    # The time of the receipt is the time of the database, in milliseconds ..
    recv_time = parse_utc(values['recv_time_iso'])
    recv_time_ms = datetime_to_ms(recv_time)

    assert publish_start_ms <= recv_time_ms <= publish_end_ms, (publish_start_ms, recv_time_ms, publish_end_ms)
    assert recv_time.microsecond % 1000 == 0, values['recv_time_iso']

    # .. and the message expires its expiration in seconds after it.
    expiration_delta = timedelta(seconds=values['expiration'])
    expiration_time = recv_time + expiration_delta
    expiration_ms = datetime_to_ms(expiration_time)

    assert values['expiration_time_iso'] == expiration_time.isoformat(), values['expiration_time_iso']
    assert values['expiration_ms'] == int(expiration_ms), values['expiration_ms']

# ################################################################################################################################

def assert_one_delivery(message:'anydict', sub_key:'str') -> 'None':
    """ A subscriber has one delivery row of a message, with the priority and expiration of the message,
    never handed out.
    """
    deliveries = _get_delivery_values(sub_key)
    assert len(deliveries) == 1, deliveries

    delivery = deliveries[0]

    expected:'anydict' = {
        'message_id': message['id'],
        'sub_key': sub_key,
        'topic_name': message['topic_name'],
        'priority': message['priority'],
        'expiration_ms': message['expiration_ms'],
        'attempt': 0,
        'leased_until_ms': 0,
    }

    assert set(delivery) == set(expected) | {'id'}, set(delivery) ^ set(expected)

    for name, value in expected.items():
        assert delivery[name] == value, (name, delivery[name], value)

    assert delivery['id'] > 0, delivery['id']

# ################################################################################################################################

def get_base_values(topic_name:'str', data:'str | None', crc32:'int', size:'int', preview:'str | None') -> 'anydict':
    """ Returns the expected values of the message row of a payload published with no optional field,
    apart from its identifier and the times.
    """
    out:'anydict' = {
        'topic_name': topic_name,
        'payload': data,
        'payload_encrypted': False,
        'payload_base64': False,
        'payload_crc32': crc32,
        'data_class': None,
        'data_size': size,
        'data_preview': preview,
        'priority': _default_priority,
        'expiration': _default_expiration,
        'publisher': None,
        'cid': None,
        'correl_id': None,
        'in_reply_to': None,
        'ext_client_id': None,
        'max_retries': None,
        'retry_sleep_time': None,
        'retry_backoff_threshold': None,
        'retry_backoff_multiplier': None,
    }

    return out

# ################################################################################################################################

def _publish_plain(backend:'SQLPubSubBackend', topic_name:'str', data:'any_') -> 'tuple[anydict, int, int]':
    """ Publishes one payload with no optional field and returns its message row with the time window of the publication.
    """
    clock = backend.clock

    publish_start_ms = clock.now_ms()
    result = backend.publish(topic_name, data)
    publish_end_ms = clock.now_ms()

    values = get_only_row(topic_name)

    # A message published without a time of its own was published when it was received.
    assert values['msg_id'] == result.msg_id
    assert values['pub_time_iso'] == values['recv_time_iso'], values

    pub_time = parse_utc(values['pub_time_iso'])
    pub_time_ms = datetime_to_ms(pub_time)

    assert values['pub_time_ms'] == int(pub_time_ms), values['pub_time_ms']

    out = values, publish_start_ms, publish_end_ms
    return out

# ################################################################################################################################

def _run_every_field(backend:'SQLPubSubBackend') -> 'None':
    """ A message published with every field has a row with each value given and one delivery row per subscriber.
    """
    backend.subscribe(_sub_key_first, _topic_fields)
    backend.subscribe(_sub_key_second, _topic_fields)

    clock = backend.clock
    publish_start_ms = clock.now_ms()

    result = backend.publish(_topic_fields_given, _data_fields,
        priority=_priority,
        expiration=_expiration,
        correl_id=_correl_id,
        in_reply_to=_in_reply_to,
        ext_client_id=_ext_client_id,
        publisher=_publisher,
        pub_time=_pub_time_iso,
        cid=_cid,
        msg_id=_msg_id_fields,
        max_retries=_max_retries,
        retry_sleep_time=_retry_sleep_time,
        retry_backoff_threshold=_retry_threshold,
        retry_backoff_multiplier=_retry_multiplier,
    )

    publish_end_ms = clock.now_ms()

    assert result.msg_id == _msg_id_fields

    # The row has each value given, with the topic in lowercase ..
    values = get_only_row(_topic_fields)

    expected:'anydict' = {
        'msg_id': _msg_id_fields,
        'topic_name': _topic_fields,
        'payload': _data_fields,
        'payload_encrypted': False,
        'payload_base64': False,
        'payload_crc32': _crc32_fields,
        'data_class': None,
        'data_size': 32,
        'data_preview': _data_fields,
        'priority': _priority,
        'expiration': _expiration,
        'pub_time_iso': _pub_time_iso,
        'pub_time_ms': _pub_time_ms,
        'publisher': _publisher,
        'cid': _cid,
        'correl_id': _correl_id,
        'in_reply_to': _in_reply_to,
        'ext_client_id': _ext_client_id,
        'max_retries': _max_retries,
        'retry_sleep_time': _retry_sleep_time,
        'retry_backoff_threshold': _retry_threshold,
        'retry_backoff_multiplier': _retry_multiplier,
    }

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)

    # .. each subscriber has one delivery row of it ..
    assert_one_delivery(values, _sub_key_first)
    assert_one_delivery(values, _sub_key_second)

    # .. and a message with its payload is not a trace.
    assert get_trace_rows(_topic_fields) == []

# ################################################################################################################################

def _run_no_optional_field(backend:'SQLPubSubBackend') -> 'None':
    """ A message published with no optional field has a row with the defaults and NULLs for the other fields.
    """
    backend.subscribe(_sub_key_first, _topic_fields)

    values, publish_start_ms, publish_end_ms = _publish_plain(backend, _topic_fields, _data_fields)

    # A new identifier was generated for the message ..
    assert values['msg_id'].startswith('zpsm.'), values['msg_id']

    expected = get_base_values(_topic_fields, _data_fields, _crc32_fields, 32, _data_fields)
    expected['msg_id'] = values['msg_id']
    expected['pub_time_iso'] = values['pub_time_iso']
    expected['pub_time_ms'] = values['pub_time_ms']

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)

    # .. and its subscriber has its delivery row.
    assert_one_delivery(values, _sub_key_first)

# ################################################################################################################################

def _assert_stored_form(data:'any_', text:'str', crc32:'int', size:'int', preview:'str | None', data_class:'str | None') -> 'None':
    """ A message published with one payload has a row with the text, checksum, size, preview and class given.
    """
    backend = _new_backend()
    backend.subscribe(_sub_key_first, _topic_forms)

    values, publish_start_ms, publish_end_ms = _publish_plain(backend, _topic_forms, data)

    expected = get_base_values(_topic_forms, text, crc32, size, preview)
    expected['msg_id'] = values['msg_id']
    expected['pub_time_iso'] = values['pub_time_iso']
    expected['pub_time_ms'] = values['pub_time_ms']
    expected['data_class'] = data_class

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)
    assert_one_delivery(values, _sub_key_first)

    # A payload of any form, the empty one included, is not a trace.
    assert get_trace_rows(_topic_forms) == []

# ################################################################################################################################

def _run_stored_forms() -> 'None':
    """ The payloads of every form are stored as their text, with the checksum, size and preview of the text.
    """

    # A dict is stored as its JSON text ..
    _assert_stored_form(_payload_dict, _payload_dict_text, _payload_dict_crc32, _payload_dict_size, _payload_dict_text, None)

    # .. a model as its JSON text, with the name of its class ..
    record = OrderRecord()
    record.order_id = 'ORD-0042'
    record.customer = 'Maria Johnson'
    record.amount = 9995

    _assert_stored_form(record, _payload_model_text, _payload_model_crc32, _payload_model_size, _payload_model_text,
        _payload_model_class)

    # .. non-ASCII text with its size in characters ..
    _assert_stored_form(_payload_non_ascii, _payload_non_ascii, _payload_non_ascii_crc32, _payload_non_ascii_size,
        _payload_non_ascii, None)

    # .. text of 1 MB with a preview of its first characters ..
    _assert_stored_form(_payload_large, _payload_large, _payload_large_crc32, _payload_large_size,
        _payload_large_preview, None)

    # .. and an empty string with no preview.
    _assert_stored_form('', '', 0, 0, None, None)

# ################################################################################################################################

def _new_encrypting_backend() -> 'tuple[SQLPubSubBackend, CryptoManager]':
    """ Returns a backend that encrypts payloads at rest, with its crypto manager, starting from empty tables.
    """
    delete_all_rows()
    delete_audit_rows()

    secret_key = CryptoManager.generate_key()
    crypto_manager = CryptoManager(secret_key=secret_key)

    backend = SQLPubSubBackend(audit_log=new_test_audit_log(), crypto_manager=crypto_manager, encrypt_at_rest=True)

    out = backend, crypto_manager
    return out

# ################################################################################################################################

def _run_encrypted_payload() -> 'None':
    """ A payload encrypted at rest is stored encrypted, with the checksum, size and preview of its text.
    """
    backend, crypto_manager = _new_encrypting_backend()
    backend.subscribe(_sub_key_first, _topic_crypto)

    values, publish_start_ms, publish_end_ms = _publish_plain(backend, _topic_crypto, _payload_non_ascii)

    # The stored payload is the encrypted text ..
    payload = values['payload']

    assert payload != _payload_non_ascii
    assert crypto_manager.decrypt(payload) == _payload_non_ascii

    # .. and every other column is as for a payload stored as it is.
    expected = get_base_values(_topic_crypto, payload, _payload_non_ascii_crc32, _payload_non_ascii_size,
        _payload_non_ascii)
    expected['msg_id'] = values['msg_id']
    expected['pub_time_iso'] = values['pub_time_iso']
    expected['pub_time_ms'] = values['pub_time_ms']
    expected['payload_encrypted'] = True

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)
    assert_one_delivery(values, _sub_key_first)

# ################################################################################################################################

def _run_nul_payload(backend:'SQLPubSubBackend') -> 'None':
    """ A payload with a NUL character is stored as the Base64 of its UTF-8 bytes, with the checksum and size of its text
    and a preview that holds the replacement character, and it is read back as it was published.
    """
    backend.subscribe(_sub_key_first, _topic_forms)

    values, publish_start_ms, publish_end_ms = _publish_plain(backend, _topic_forms, _payload_nul)

    # The row holds the Base64 of the payload ..
    expected = get_base_values(_topic_forms, _payload_nul_base64, _payload_nul_crc32, _payload_nul_size,
        _payload_nul_preview)
    expected['msg_id'] = values['msg_id']
    expected['pub_time_iso'] = values['pub_time_iso']
    expected['pub_time_ms'] = values['pub_time_ms']
    expected['payload_base64'] = True

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)
    assert_one_delivery(values, _sub_key_first)

    # .. and the payload is read back with its NUL character.
    message = {'sequence_id': values['id']}
    assert backend.read_payload(message) == _payload_nul

# ################################################################################################################################

def _run_no_subscribers() -> 'None':
    """ A message of a topic without subscribers is stored without its payload, encrypted or not, as a trace
    with no delivery rows.
    """
    backend, _ = _new_encrypting_backend()

    values, publish_start_ms, publish_end_ms = _publish_plain(backend, _topic_no_subs, _payload_non_ascii)

    expected = get_base_values(_topic_no_subs, None, _payload_non_ascii_crc32, _payload_non_ascii_size,
        _payload_non_ascii)
    expected['msg_id'] = values['msg_id']
    expected['pub_time_iso'] = values['pub_time_iso']
    expected['pub_time_ms'] = values['pub_time_ms']

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)

    # No subscriber has a delivery row of it ..
    assert get_delivery_rows(_sub_key_first) == []

    # .. and it is a trace from the start.
    traces = get_trace_rows(_topic_no_subs)
    assert len(traces) == 1, traces

    trace = dict(traces[0]._mapping)
    assert trace == {'message_id': values['id'], 'topic_name': _topic_no_subs, 'pub_time_ms': values['pub_time_ms']}

# ################################################################################################################################

def _build(backend:'SQLPubSubBackend', topic_name:'str', data:'str') -> 'BuiltPublication':
    """ Builds a publication of the message identifier that the repeat parts share.
    """
    out = build_publication(backend, topic_name, data, msg_id=_msg_id_repeat)
    return out

# ################################################################################################################################

def _run_repeated_publication(backend:'SQLPubSubBackend') -> 'None':
    """ A publication that repeats an existing message with the same topic and payload is a repeat that writes nothing,
    while one with another payload or another topic fails its own publisher alone with PubSubDuplicateMsgID.
    """
    backend.subscribe(_sub_key_first, _topic_repeat)

    original = _build(backend, _topic_repeat, _data_repeat)
    backend._writer.publish(original.pending)

    assert not original.pending.is_repeat
    assert original.pending.subscriber_keys == [_sub_key_first]

    original_values = get_only_row(_topic_repeat)

    # The same message published again is a repeat, with no subscribers to wake up ..
    repeated = _build(backend, _topic_repeat, _data_repeat)
    backend._writer.publish(repeated.pending)

    assert repeated.pending.is_repeat
    assert repeated.pending.exception is None
    assert repeated.pending.subscriber_keys == []

    # .. which a publisher receives as the result of the original publication ..
    result = backend.publish(_topic_repeat, _data_repeat, msg_id=_msg_id_repeat)
    assert result.msg_id == _msg_id_repeat

    # .. another payload or another topic under the same identifier fails the publisher ..
    for topic_name, data in ((_topic_repeat, _data_different), (_topic_other, _data_repeat)):
        try:
            _ = backend.publish(topic_name, data, msg_id=_msg_id_repeat)
        except PubSubDuplicateMsgID as e:
            assert _msg_id_repeat in str(e), e
        else:
            raise Exception(f'Expected PubSubDuplicateMsgID for {topic_name} and {data}')

    # .. and nothing of any of them was written.
    assert get_only_row(_topic_repeat) == original_values
    assert get_message_rows(_topic_other) == []
    assert len(get_delivery_rows(_sub_key_first)) == 1

# ################################################################################################################################

def _run_repeats_in_one_commit(backend:'SQLPubSubBackend') -> 'None':
    """ Two publications of one identifier in one commit insert one message, the second one being a repeat
    with the same payload and failing alone with another payload.
    """
    backend.subscribe(_sub_key_first, _topic_repeat)

    # The same payload twice inserts one message ..
    first = _build(backend, _topic_repeat, _data_repeat)
    second = _build(backend, _topic_repeat, _data_repeat)

    write_in_one_commit(backend, [first.pending, second.pending])

    assert not first.pending.is_repeat
    assert first.pending.exception is None
    assert first.pending.subscriber_keys == [_sub_key_first]

    assert second.pending.is_repeat
    assert second.pending.exception is None
    assert second.pending.subscriber_keys == []

    values = get_only_row(_topic_repeat)
    assert values['payload'] == _data_repeat

    assert_one_delivery(values, _sub_key_first)

    # .. and another payload in the commit that inserts the first one fails alone.
    delete_all_rows()
    backend.subscribe(_sub_key_first, _topic_repeat)

    first = _build(backend, _topic_repeat, _data_repeat)
    different = _build(backend, _topic_repeat, _data_different)

    write_in_one_commit(backend, [first.pending, different.pending])

    assert first.pending.exception is None
    assert not different.pending.is_repeat
    assert isinstance(different.pending.exception, PubSubDuplicateMsgID), different.pending.exception

    values = get_only_row(_topic_repeat)
    assert values['payload'] == _data_repeat

    assert_one_delivery(values, _sub_key_first)

# ################################################################################################################################

def _run_repeat_of_removed_message(backend:'SQLPubSubBackend') -> 'None':
    """ A repeat of a message that the cleanup removed after the insert of the repeat met it is a repeat that writes
    nothing. The cleanup runs between the two statements as a concurrent writer. The original has a dedup record
    that expires the moment it is written, so the repeat replaces it and goes on to the insert of its message.
    """
    backend.subscribe(_sub_key_first, _topic_repeat)

    # The original message is fully delivered, which makes it a trace that the cleanup may remove ..
    with env_value(Env_Dedup_Window_Days, _no_dedup_window_days):
        original = _build(backend, _topic_repeat, _data_repeat)

    backend._writer.publish(original.pending)

    _ = backend.ack_messages(_sub_key_first, [_msg_id_repeat])
    assert len(get_trace_rows(_topic_repeat)) == 1

    # .. the cleanup runs once the insert of the repeat met the original message ..
    engine = get_database_engine()
    cleanup_results:'anylist' = []

    def _on_message_insert(*args:'any_') -> 'None':
        statement = args[2]

        if not cleanup_results:
            if statement.startswith('INSERT INTO pubsub_message'):
                cleanup_results.append('started')

                old_value = os.environ.get(Env_Delivered_Max_Messages)
                os.environ[Env_Delivered_Max_Messages] = _no_delivered_messages

                try:
                    counts = PubSubCleanup().sweep_once()
                finally:
                    if old_value is None:
                        del os.environ[Env_Delivered_Max_Messages]
                    else:
                        os.environ[Env_Delivered_Max_Messages] = old_value

                cleanup_results.append(counts)

    event.listen(engine, 'after_cursor_execute', _on_message_insert)

    try:
        repeated = _build(backend, _topic_repeat, _data_repeat)
        backend._writer.publish(repeated.pending)
    finally:
        event.remove(engine, 'after_cursor_execute', _on_message_insert)

    # .. so the original message is gone by the time the repeat looks it up ..
    counts = cleanup_results[1]
    assert counts['over_cap'] == 1, counts

    # .. and the repeat is a repeat all the same, which writes nothing.
    assert repeated.pending.is_repeat
    assert repeated.pending.exception is None
    assert repeated.pending.subscriber_keys == []

    assert get_message_rows(_topic_repeat) == []
    assert get_delivery_rows(_sub_key_first) == []

# ################################################################################################################################

def run_publish_values_scenario() -> 'None':
    """ The rows that publications write, each part starting from empty tables.
    """
    _run_every_field(_new_backend())
    _run_no_optional_field(_new_backend())
    _run_stored_forms()
    _run_encrypted_payload()
    _run_nul_payload(_new_backend())
    _run_no_subscribers()
    _run_repeated_publication(_new_backend())
    _run_repeats_in_one_commit(_new_backend())
    _run_repeat_of_removed_message(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
