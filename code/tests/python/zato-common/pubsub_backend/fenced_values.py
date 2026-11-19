# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rows that fenced acknowledgements write and remove, column by column for the receipts they publish,
# and the items that fail for each reason, which write nothing and fail their own callers alone.

# stdlib
import os
from time import sleep

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_message_rows, write_in_one_commit
from publish_values import assert_message_row, assert_one_delivery, get_only_row
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_atomic
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.util.time_ import datetime_to_ms, parse_utc

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    BuiltPublication = BuiltPublication
    callable_ = callable_
    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

Env_Pull_Lease_Seconds = ModuleCtx.Env_Pull_Lease_Seconds

# The topics and subscribers of the scenario
_topic_input  = 'pubsub.backend.test.fenced-values.input'
_topic_output = 'pubsub.backend.test.fenced-values.output'

_sub_key_input  = 'zpsk.test.fenced-values.input'
_sub_key_output = 'zpsk.test.fenced-values.output'

# The payloads of the input messages and of the receipts
_data_input   = 'Order ORD-0042 for Maria Johnson'
_data_receipt = 'Receipt RCP-0042 for Maria Johnson'
_data_other   = 'Receipt RCP-0043 for John Smith'

# The checksum, size and fields of the receipt published with every field
_receipt_msg_id     = 'zpsm.test.fenced-values.receipt'
_receipt_crc32      = 277004779
_receipt_size       = 34
_receipt_priority   = 8
_receipt_expiration = 7200
_receipt_cid        = 'cid-fenced-values-1'
_receipt_correl_id  = 'correl-fenced-values-1'
_receipt_publisher  = 'publisher.receipts'

# The identifiers of the receipts of the other parts
_receipt_msg_id_other = 'zpsm.test.fenced-values.receipt-other'

# The delivery attempt that no pull handed out
_stale_attempt = 5

# How long the leases of the parts in which a lease runs out are, in seconds
_lease_seconds_none = '0'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables, with one subscriber of the input topic
    and one of the output topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    out.subscribe(_sub_key_input, _topic_input)
    out.subscribe(_sub_key_output, _topic_output)

    return out

# ################################################################################################################################

def _publish_and_pull(backend:'SQLPubSubBackend') -> 'tuple[str, int]':
    """ Publishes one input message, pulls it and returns its identifier with the attempt it was handed out with.
    """
    result = backend.publish(_topic_input, _data_input)
    messages = backend.pull_messages(_sub_key_input)

    assert len(messages) == 1, messages

    message = messages[0]
    assert message['msg_id'] == result.msg_id

    out = message['msg_id'], message['delivery_attempt']
    return out

# ################################################################################################################################

def _get_input_rows() -> 'anylist':
    """ Returns the values of the delivery rows of the input subscriber, by column.
    """
    out:'anylist' = []

    for row in get_delivery_rows(_sub_key_input):
        values = dict(row._mapping)
        out.append(values)

    return out

# ################################################################################################################################

def _get_output_msg_ids() -> 'strlist':
    """ Returns the identifiers of the messages of the output topic, in the order of publication.
    """
    out:'strlist' = []

    for row in get_message_rows(_topic_output):
        out.append(row.msg_id)

    return out

# ################################################################################################################################

def _with_lease_seconds(func:'callable_', *args:'any_') -> 'any_':
    """ Runs a function with the given arguments while the pulls lease their messages for no time at all.
    """
    os.environ[Env_Pull_Lease_Seconds] = _lease_seconds_none

    try:
        out = func(*args)
    finally:
        del os.environ[Env_Pull_Lease_Seconds]

    return out

# ################################################################################################################################

def _assert_fails(func:'callable_', exception_class:'type[Exception]', snapshot:'anylist') -> 'None':
    """ A fenced acknowledgement fails its caller with the given exception and writes nothing.
    """
    output_msg_ids = _get_output_msg_ids()

    try:
        _ = func()
    except exception_class:
        pass
    else:
        raise Exception(f'Expected {exception_class.__name__}')

    assert _get_input_rows() == snapshot
    assert _get_output_msg_ids() == output_msg_ids

# ################################################################################################################################

def _build_receipt(backend:'SQLPubSubBackend', msg_id:'str', data:'str') -> 'BuiltPublication':
    """ Builds a receipt of an input message with no optional field.
    """
    out = build_publication(backend, _topic_output, data, msg_id=msg_id)
    return out

# ################################################################################################################################

def _run_receipt_values(backend:'SQLPubSubBackend') -> 'None':
    """ A fenced acknowledgement removes the delivery row it is about and publishes its receipt with every value given,
    with one delivery row per subscriber of the output topic.
    """
    msg_id, attempt = _publish_and_pull(backend)

    clock = backend.clock
    publish_start_ms = clock.now_ms()

    built = build_publication(backend, _topic_output, _data_receipt,
        priority=_receipt_priority,
        expiration=_receipt_expiration,
        correl_id=_receipt_correl_id,
        publisher=_receipt_publisher,
        cid=_receipt_cid,
        msg_id=_receipt_msg_id,
    )

    result = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, attempt)], [built])
    publish_end_ms = clock.now_ms()

    # The acknowledgement removed the delivery row of the input message ..
    assert result.removed_count == 1
    assert result.published == [_receipt_msg_id]
    assert _get_input_rows() == []

    # .. whose payload no subscriber needs anymore ..
    input_rows = get_message_rows(_topic_input)
    assert input_rows[0].payload is None

    # .. and the receipt has a row of its own with the values given ..
    values = get_only_row(_topic_output)

    expected:'anydict' = {
        'msg_id': _receipt_msg_id,
        'topic_name': _topic_output,
        'payload': _data_receipt,
        'payload_encrypted': False,
        'payload_crc32': _receipt_crc32,
        'data_class': None,
        'data_size': _receipt_size,
        'data_preview': _data_receipt,
        'priority': _receipt_priority,
        'expiration': _receipt_expiration,
        'pub_time_iso': values['recv_time_iso'],
        'pub_time_ms': values['pub_time_ms'],
        'publisher': _receipt_publisher,
        'cid': _receipt_cid,
        'correl_id': _receipt_correl_id,
        'in_reply_to': None,
        'ext_client_id': None,
        'max_retries': None,
        'retry_sleep_time': None,
        'retry_backoff_threshold': None,
        'retry_backoff_multiplier': None,
    }

    assert_message_row(values, expected, publish_start_ms, publish_end_ms)

    pub_time = parse_utc(values['pub_time_iso'])
    pub_time_ms = datetime_to_ms(pub_time)

    assert values['pub_time_ms'] == int(pub_time_ms), values['pub_time_ms']

    # .. with a delivery row for the subscriber of the output topic.
    assert_one_delivery(values, _sub_key_output)

# ################################################################################################################################

def _run_stale_attempt(backend:'SQLPubSubBackend') -> 'None':
    """ An acknowledgement with an attempt that no pull handed out fails with PubSubAckConflict and writes nothing.
    """
    msg_id, _ = _publish_and_pull(backend)
    snapshot = _get_input_rows()

    def _ack() -> 'None':
        built = _build_receipt(backend, _receipt_msg_id, _data_receipt)
        _ = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, _stale_attempt)], [built])

    _assert_fails(_ack, PubSubAckConflict, snapshot)

# ################################################################################################################################

def _run_lease_ran_out(backend:'SQLPubSubBackend') -> 'None':
    """ A message whose lease ran out is acknowledged with its attempt as long as no pull handed it out again,
    after which only the attempt of the latest pull is.
    """

    # A lease that ran out without another pull leaves the attempt as it was, which the acknowledgement holds ..
    msg_id, attempt = _with_lease_seconds(_publish_and_pull, backend)
    sleep(0.01)

    built = _build_receipt(backend, _receipt_msg_id, _data_receipt)
    result = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, attempt)], [built])

    assert result.removed_count == 1
    assert _get_input_rows() == []
    assert _get_output_msg_ids() == [_receipt_msg_id]

    # .. whereas a message handed out again belongs to the latest pull ..
    msg_id, first_attempt = _with_lease_seconds(_publish_and_pull, backend)
    sleep(0.01)

    messages = backend.pull_messages(_sub_key_input)
    second_attempt = messages[0]['delivery_attempt']

    assert second_attempt == first_attempt + 1

    snapshot = _get_input_rows()
    assert snapshot[0]['attempt'] == second_attempt

    def _ack_first() -> 'None':
        built = _build_receipt(backend, _receipt_msg_id_other, _data_other)
        _ = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, first_attempt)], [built])

    _assert_fails(_ack_first, PubSubAckConflict, snapshot)

    # .. which acknowledges it.
    built = _build_receipt(backend, _receipt_msg_id_other, _data_other)
    result = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, second_attempt)], [built])

    assert result.removed_count == 1
    assert _get_input_rows() == []
    assert _get_output_msg_ids() == [_receipt_msg_id, _receipt_msg_id_other]

# ################################################################################################################################

def _run_concluded(backend:'SQLPubSubBackend') -> 'None':
    """ An acknowledgement of a message concluded already fails with PubSubAckConflict if it publishes a new message,
    and with the same publications as the acknowledgement that concluded it, it succeeds and writes nothing.
    """
    msg_id, attempt = _publish_and_pull(backend)

    built = _build_receipt(backend, _receipt_msg_id, _data_receipt)
    _ = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, attempt)], [built])

    # A new receipt for the concluded message ..
    def _ack_new() -> 'None':
        built = _build_receipt(backend, _receipt_msg_id_other, _data_other)
        _ = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, attempt)], [built])

    _assert_fails(_ack_new, PubSubAckConflict, [])

    # .. and the same receipt again, which the writer records as concluded.
    built = _build_receipt(backend, _receipt_msg_id, _data_receipt)

    ack = new_fenced_ack(_sub_key_input, [msg_id], [attempt])
    atomic = new_pending_atomic([built.pending], ack, True)

    backend._writer.ack_atomic(atomic)

    assert atomic.exception is None
    assert ack.removed_count == 0
    assert ack.concluded_msg_ids == [msg_id]
    assert built.pending.is_repeat
    assert _get_output_msg_ids() == [_receipt_msg_id]

# ################################################################################################################################

def _run_receipt_id_strict(backend:'SQLPubSubBackend') -> 'None':
    """ A receipt of a pull client whose identifier stands for a different message fails the whole acknowledgement
    with PubSubDuplicateMsgID, which writes nothing.
    """
    _ = backend.publish(_topic_output, _data_other, msg_id=_receipt_msg_id)

    msg_id, attempt = _publish_and_pull(backend)
    snapshot = _get_input_rows()

    def _ack() -> 'None':
        built = _build_receipt(backend, _receipt_msg_id, _data_receipt)
        _ = backend.ack_pulled_with_publications(_sub_key_input, [(msg_id, attempt)], [built])

    _assert_fails(_ack, PubSubDuplicateMsgID, snapshot)

    output_rows = get_message_rows(_topic_output)
    assert output_rows[0].payload == _data_other

# ################################################################################################################################

def _run_receipt_id_not_strict(backend:'SQLPubSubBackend') -> 'None':
    """ A publication of a push subscriber whose identifier stands for a different message is the only part
    of its acknowledgement not written, and it alone receives PubSubDuplicateMsgID.
    """
    _ = backend.publish(_topic_output, _data_other, msg_id=_receipt_msg_id)

    msg_id, _ = _publish_and_pull(backend)

    conflicting = _build_receipt(backend, _receipt_msg_id, _data_receipt)
    accepted = _build_receipt(backend, _receipt_msg_id_other, _data_receipt)

    publications = [conflicting.pending, accepted.pending]
    backend.ack_with_publications(_sub_key_input, [msg_id], publications, [])

    # The acknowledgement and the other publication were written ..
    assert _get_input_rows() == []
    assert accepted.pending.exception is None
    assert _get_output_msg_ids() == [_receipt_msg_id, _receipt_msg_id_other]

    # .. and the conflicting publication alone was not.
    assert isinstance(conflicting.pending.exception, PubSubDuplicateMsgID), conflicting.pending.exception

    output_rows = get_message_rows(_topic_output)
    assert output_rows[0].payload == _data_other

# ################################################################################################################################

def _run_isolated_in_commit(backend:'SQLPubSubBackend') -> 'None':
    """ A fenced acknowledgement that fails in a commit shared with a plain publication fails alone,
    and the publication is written.
    """
    msg_id, _ = _publish_and_pull(backend)
    snapshot = _get_input_rows()

    receipt = _build_receipt(backend, _receipt_msg_id, _data_receipt)
    plain = _build_receipt(backend, _receipt_msg_id_other, _data_other)

    ack = new_fenced_ack(_sub_key_input, [msg_id], [_stale_attempt])
    atomic = new_pending_atomic([receipt.pending], ack, True)

    write_in_one_commit(backend, [atomic, plain.pending])

    assert isinstance(atomic.exception, PubSubAckConflict), atomic.exception
    assert plain.pending.exception is None

    assert _get_input_rows() == snapshot
    assert _get_output_msg_ids() == [_receipt_msg_id_other]

# ################################################################################################################################

def run_fenced_values_scenario() -> 'None':
    """ The rows that fenced acknowledgements write and remove, each part starting from empty tables.
    """
    _run_receipt_values(_new_backend())
    _run_stale_attempt(_new_backend())
    _run_lease_ran_out(_new_backend())
    _run_concluded(_new_backend())
    _run_receipt_id_strict(_new_backend())
    _run_receipt_id_not_strict(_new_backend())
    _run_isolated_in_commit(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
