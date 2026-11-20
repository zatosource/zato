# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit events of publications, of the push deliveries that a fenced acknowledgement concludes and of the receipts
# that it publishes, column by column, with the receipts recorded only when their acknowledgement is written,
# the events of the outgoing calls of push subscriber services, recorded before each call returns,
# and the events that the export receives.

# SQLAlchemy
from sqlalchemy import select

# Zato
from common import delete_all_rows, delete_audit_rows, get_event_rows, get_message_rows
from zato.common.audit_log.api import event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.export.state import set_audit_export
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.delivery_scope import close_delivery_scope, open_delivery_scope
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID
from zato.common.test.audit_log_ import new_test_audit_log, ModuleCtx as AuditModuleCtx, RecordingAuditExport
from zato.common.util.time_ import parse_utc, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, strset

    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    intlist = intlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers of the scenario
_topic_input  = 'pubsub.backend.test.publish-events.input'
_topic_output = 'pubsub.backend.test.publish-events.output'
_topic_off    = 'pubsub.backend.test.publish-events.off'

_sub_key_input  = 'zpsk.test.publish-events.input'
_sub_key_output = 'zpsk.test.publish-events.output'

# The values of a message published with every field that an event records
_data          = 'Order ORD-0042 for Maria Johnson'
_size          = 32
_priority      = 7
_cid           = 'cid-publish-events-1'
_correl_id     = 'correl-publish-events-1'
_ext_client_id = 'client-maria-johnson'
_publisher     = 'publisher.orders'
_msg_id        = 'zpsm.test.publish-events.order'

# The receipts that the acknowledgements publish
_receipt_data   = 'Receipt RCP-0042 for Maria Johnson'
_receipt_size   = 34
_receipt_msg_id = 'zpsm.test.publish-events.receipt'
_other_msg_id   = 'zpsm.test.publish-events.receipt-other'

# The endpoint that a push subscriber delivers to
_push_endpoint = 'orders.process'

# The outgoing REST connection that a push subscriber service calls, its address and the request that it sends
_outgoing_name     = 'pubsub.backend.test.publish-events.orders-api'
_outgoing_endpoint = 'https://orders.example.com/api/orders'
_outgoing_data     = '{"order_id": "ORD-0042", "customer": "Maria Johnson"}'

# Every column of an event, with the text of its payload
_event_columns:'strset' = set(event_table.c.keys()) | {'data'}

# The columns of an event whose values follow from the time and the payload store of its commit
_derived_columns:'strset' = {'id', 'event_time', 'payload_id'}

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

def _get_only_event(topic_name:'str', event_type:'str') -> 'anydict':
    """ Returns the only event of one type about one topic.
    """
    events = get_event_rows(topic_name, event_type)
    assert len(events) == 1, events

    out = events[0]
    return out

# ################################################################################################################################

def _get_expected(event_type:'str', topic_name:'str', message:'anydict', **values:'any_') -> 'anydict':
    """ Returns the expected values of an event about one message, with the given values in place of the defaults.
    """
    out:'anydict' = {
        'cid': '',
        'cid_sequence': 0,
        'source': AuditSource.PubSub,
        'event_type': event_type,
        'object_name': topic_name,
        'msg_id': message['msg_id'],
        'correl_id': '',
        'ext_client_id': '',
        'pub_time': parse_utc(message['pub_time_iso']),
        'server_name': AuditModuleCtx.Server_Name,
        'endpoint': '',
        'sub_key': '',
        'size': message['data_size'],
        'priority': message['priority'],
        'outcome': AuditOutcome.OK,
        'application_outcome': '',
        'classification': '',
        'status': '',
        'duration_ms': 0,
        'internal_data': '',
        'data': message['payload'],
    }

    out.update(values)
    return out

# ################################################################################################################################

def _assert_event(event:'anydict', expected:'anydict', start:'any_', end:'any_') -> 'None':
    """ An event has the expected value in each column, and the time of its event within the given window.
    """
    assert set(event) == _event_columns, set(event) ^ _event_columns

    expected_columns = set(expected) | _derived_columns
    assert expected_columns == _event_columns, expected_columns ^ _event_columns

    for name, value in expected.items():
        assert event[name] == value, (name, event[name], value)

    assert event['id'] > 0, event['id']
    assert event['payload_id'] is not None
    assert start <= event['event_time'] <= end, (start, event['event_time'], end)

# ################################################################################################################################

def _get_message_values(topic_name:'str', msg_id:'str') -> 'anydict':
    """ Returns the values of the message row of one message identifier.
    """
    for row in get_message_rows(topic_name):
        if row.msg_id == msg_id:
            out = dict(row._mapping)
            break
    else:
        raise Exception(f'No message row for {msg_id}')

    return out

# ################################################################################################################################

def _run_publication_events(backend:'SQLPubSubBackend') -> 'None':
    """ A publication has one event with the values of its message, and the repeat of a publication, a publication
    that fails and a publication to a topic whose audit log is off have none.
    """
    start = utcnow()

    _ = backend.publish(_topic_input, _data, priority=_priority, cid=_cid, correl_id=_correl_id,
        ext_client_id=_ext_client_id, publisher=_publisher, msg_id=_msg_id)

    end = utcnow()

    # The event records each value of the message, with its publisher as the endpoint ..
    message = _get_message_values(_topic_input, _msg_id)
    event = _get_only_event(_topic_input, AuditEvent.Published)

    expected = _get_expected(AuditEvent.Published, _topic_input, message, cid=_cid, cid_sequence=1,
        correl_id=_correl_id, ext_client_id=_ext_client_id, endpoint=_publisher)

    _assert_event(event, expected, start, end)
    assert event['size'] == _size

    # .. a repeat of the publication and a publication that fails record nothing ..
    _ = backend.publish(_topic_input, _data, priority=_priority, cid=_cid, correl_id=_correl_id,
        ext_client_id=_ext_client_id, publisher=_publisher, msg_id=_msg_id)

    try:
        _ = backend.publish(_topic_input, _receipt_data, msg_id=_msg_id)
    except PubSubDuplicateMsgID:
        pass
    else:
        raise Exception('Expected PubSubDuplicateMsgID')

    assert len(get_event_rows(_topic_input, AuditEvent.Published)) == 1

    # .. and neither does a publication to a topic whose audit log is off.
    backend.set_topic_audit_flag(_topic_off, False)
    _ = backend.publish(_topic_off, _data)

    assert get_event_rows(_topic_off, AuditEvent.Published) == []

# ################################################################################################################################

def _deliver_batch(backend:'SQLPubSubBackend', msg_id:'str', receipt_msg_id:'str') -> 'None':
    """ Delivers one message to a push subscriber as a batch of its own, recording its delivery and publishing
    a receipt in the scope of the batch, and acknowledges the batch with the receipt. The delivery carries the payload
    of the message as it was published, which its row no longer holds once the message is acknowledged.
    """
    message = _get_message_values(_topic_input, msg_id)
    pub_time = parse_utc(message['pub_time_iso'])

    scope = open_delivery_scope()

    try:
        _ = backend.publish(_topic_output, _receipt_data, msg_id=receipt_msg_id)

        _ = backend.audit_log.insert(AuditSource.PubSub, AuditEvent.Delivered, _topic_input,
            msg_id=msg_id,
            pub_time=pub_time,
            endpoint=_push_endpoint,
            sub_key=_sub_key_input,
            size=message['data_size'],
            priority=message['priority'],
            outcome=AuditOutcome.OK,
            data=_data,
            commits_with_batch=True,
        )

    finally:
        close_delivery_scope()

    backend.ack_with_publications(_sub_key_input, [msg_id], scope.publications, scope.audit_events)

# ################################################################################################################################

def _run_push_batch_events(backend:'SQLPubSubBackend') -> 'None':
    """ The delivery of a push batch and its receipts are recorded when the batch is acknowledged, and a batch whose
    acknowledgement fails records its delivery alone.
    """
    result = backend.publish(_topic_input, _data)
    message = _get_message_values(_topic_input, result.msg_id)

    start = utcnow()
    _deliver_batch(backend, result.msg_id, _receipt_msg_id)
    end = utcnow()

    # The delivery is recorded with its subscriber and its endpoint ..
    event = _get_only_event(_topic_input, AuditEvent.Delivered)

    expected = _get_expected(AuditEvent.Delivered, _topic_input, message, endpoint=_push_endpoint,
        sub_key=_sub_key_input)

    _assert_event(event, expected, start, end)

    # .. and so is the receipt that it published ..
    receipt = _get_message_values(_topic_output, _receipt_msg_id)
    event = _get_only_event(_topic_output, AuditEvent.Published)

    expected = _get_expected(AuditEvent.Published, _topic_output, receipt)
    _assert_event(event, expected, start, end)

    assert event['size'] == _receipt_size

    # .. whereas the delivery of a concluded message with a new receipt fails, recording the delivery alone.
    try:
        _deliver_batch(backend, result.msg_id, _other_msg_id)
    except PubSubAckConflict:
        pass
    else:
        raise Exception('Expected PubSubAckConflict')

    assert len(get_event_rows(_topic_input, AuditEvent.Delivered)) == 2
    assert len(get_event_rows(_topic_output, AuditEvent.Published)) == 1

    output_rows = get_message_rows(_topic_output)
    assert len(output_rows) == 1, output_rows

# ################################################################################################################################

def _get_outgoing_event_ids() -> 'intlist':
    """ Returns the ids of the events of the outgoing REST connection of the scenario, in the order of their ids.
    """
    engine = get_database_engine()

    query = select(event_table.c.id)
    query = query.where(event_table.c.source == AuditSource.REST_Outgoing)
    query = query.where(event_table.c.object_name == _outgoing_name)
    query = query.order_by(event_table.c.id)

    out:'intlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row.id)

    return out

# ################################################################################################################################

def _run_outgoing_events_in_batch(backend:'SQLPubSubBackend') -> 'None':
    """ The event of an outgoing call that a push subscriber service makes commits before the call returns,
    whereas the event that concludes a message waits for the acknowledgement of its batch.
    """
    result = backend.publish(_topic_input, _data)
    audit_log = backend.audit_log

    scope = open_delivery_scope()

    try:

        # The event of the outgoing call commits at once and its id is returned ..
        event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _outgoing_name,
            endpoint=_outgoing_endpoint,
            outcome=AuditOutcome.OK,
            data=_outgoing_data,
        )

        assert event_id is not None
        assert _get_outgoing_event_ids() == [event_id]
        assert scope.audit_events == []

        # .. while the event that concludes the message stays in the scope of the batch.
        delivered_id = audit_log.insert(AuditSource.PubSub, AuditEvent.Delivered, _topic_input,
            msg_id=result.msg_id,
            sub_key=_sub_key_input,
            outcome=AuditOutcome.OK,
            data=_data,
            commits_with_batch=True,
        )

        assert delivered_id is None
        assert get_event_rows(_topic_input, AuditEvent.Delivered) == []

        scope_event_count = len(scope.audit_events)
        assert scope_event_count == 1

    finally:
        close_delivery_scope()

    # A batch that is never acknowledged leaves the event of the outgoing call behind.
    assert _get_outgoing_event_ids() == [event_id]
    assert get_event_rows(_topic_input, AuditEvent.Delivered) == []

# ################################################################################################################################

def _run_pull_ack_events(backend:'SQLPubSubBackend') -> 'None':
    """ The receipts of a pull client are recorded when its acknowledgement is written and not when it fails.
    """
    result = backend.publish(_topic_input, _data)
    messages = backend.pull_messages(_sub_key_input)
    attempt = messages[0]['delivery_attempt']

    # A failing acknowledgement records no receipt ..
    built = build_publication(backend, _topic_output, _receipt_data, msg_id=_receipt_msg_id)

    try:
        _ = backend.ack_pulled_with_publications(_sub_key_input, [(result.msg_id, attempt + 1)], [built])
    except PubSubAckConflict:
        pass
    else:
        raise Exception('Expected PubSubAckConflict')

    assert get_event_rows(_topic_output, AuditEvent.Published) == []

    # .. and a written one records its receipt.
    start = utcnow()

    built = build_publication(backend, _topic_output, _receipt_data, msg_id=_receipt_msg_id)
    _ = backend.ack_pulled_with_publications(_sub_key_input, [(result.msg_id, attempt)], [built])

    end = utcnow()

    receipt = _get_message_values(_topic_output, _receipt_msg_id)
    event = _get_only_event(_topic_output, AuditEvent.Published)

    expected = _get_expected(AuditEvent.Published, _topic_output, receipt)
    _assert_event(event, expected, start, end)

# ################################################################################################################################

def _get_exports(export:'RecordingAuditExport', event_type:'str') -> 'anylist':
    """ Returns the events of one type that the export received, in the order it received them.
    """
    out:'anylist' = []

    for event in export.events:
        if event.values['event_type'] == event_type:
            out.append(event)

    return out

# ################################################################################################################################

def _with_export(func:'callable_') -> 'RecordingAuditExport':
    """ Runs a function with an export that records the events of each commit, and returns the export.
    """
    out = RecordingAuditExport()
    set_audit_export(out)

    try:
        func()
    finally:
        set_audit_export(None)

    return out

# ################################################################################################################################

def _run_export(backend:'SQLPubSubBackend') -> 'None':
    """ The export receives each event of a publication, a push batch and its receipts with its id, and with its payload
    when its topic exports payloads.
    """
    backend.set_topic_payload_flag(_topic_output, True)

    result = backend.publish(_topic_input, _data)

    def _deliver() -> 'None':
        _deliver_batch(backend, result.msg_id, _receipt_msg_id)

    export = _with_export(_deliver)

    # The delivery is exported without its payload ..
    delivered = get_event_rows(_topic_input, AuditEvent.Delivered)
    exported = _get_exports(export, AuditEvent.Delivered)

    assert len(exported) == 1, exported
    assert exported[0].event_id == delivered[0]['id']
    assert not exported[0].is_export_payload_active

    # .. and the receipt of a topic that exports payloads with it.
    published = get_event_rows(_topic_output, AuditEvent.Published)
    exported = _get_exports(export, AuditEvent.Published)

    assert len(exported) == 1, exported
    assert exported[0].event_id == published[0]['id']
    assert exported[0].is_export_payload_active
    assert exported[0].values['msg_id'] == _receipt_msg_id
    assert exported[0].values['data'] == _receipt_data

# ################################################################################################################################

def run_publish_events_scenario() -> 'None':
    """ The audit events of publications and of fenced acknowledgements, each part starting from empty tables.
    """
    _run_publication_events(_new_backend())
    _run_push_batch_events(_new_backend())
    _run_outgoing_events_in_batch(_new_backend())
    _run_pull_ack_events(_new_backend())
    _run_export(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
